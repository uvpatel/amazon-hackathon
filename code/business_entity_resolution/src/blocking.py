"""Candidate generation / blocking strategies with multi-rule inverted indexing."""

from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple
import pandas as pd
from .normalization import (
    normalize_name,
    get_core_name_tokens,
    normalize_address,
    normalize_country,
    extract_numeric_tokens,
)


class BlockingIndex:
    """Multi-rule inverted index over target candidate entities (Source 2 and Source 3)."""

    def __init__(self, max_token_freq: int = 1000):
        self.max_token_freq = max_token_freq
        self.exact_name_index: Dict[str, Set[str]] = defaultdict(set)
        self.core_token_index: Dict[str, Set[str]] = defaultdict(set)
        self.prefix_index: Dict[str, Set[str]] = defaultdict(set)
        self.address_num_index: Dict[Tuple[str, str], Set[str]] = defaultdict(set)
        self.pool_records: Dict[str, Tuple[str, str, str]] = {}

    def build_from_dataframe(self, pool_df: pd.DataFrame) -> None:
        """Populate inverted indexes from candidate pool dataframe."""
        for _, row in pool_df.iterrows():
            eid = str(row["entity_id"]).strip()
            raw_name = str(row.get("business_name", ""))
            raw_addr = str(row.get("business_address", ""))
            raw_country = str(row.get("country", ""))

            norm_name = normalize_name(raw_name)
            norm_addr = normalize_address(raw_addr)
            norm_country = normalize_country(raw_country)
            core_tokens = get_core_name_tokens(norm_name)
            numeric_tokens = extract_numeric_tokens(norm_addr)

            # Store compact tuple (norm_name, norm_addr, norm_country)
            self.pool_records[eid] = (norm_name, norm_addr, norm_country)

            # 1. Exact normalized name
            if norm_name:
                self.exact_name_index[norm_name].add(eid)

            # 2. Core name tokens
            for token in core_tokens:
                if len(token) >= 3:
                    self.core_token_index[token].add(eid)

            # 3. Name 4-char prefix
            if norm_name and len(norm_name) >= 4:
                prefix = norm_name[:4]
                self.prefix_index[prefix].add(eid)

            # 4. Country + Numeric address tokens
            for num in numeric_tokens:
                self.address_num_index[(norm_country, num)].add(eid)

        # Prune overly generic tokens to prevent candidate explosion
        self.core_token_index = {
            t: eids for t, eids in self.core_token_index.items()
            if len(eids) <= self.max_token_freq
        }
        self.prefix_index = {
            p: eids for p, eids in self.prefix_index.items()
            if len(eids) <= self.max_token_freq
        }


def retrieve_candidates_for_s1(
    s1_row: Dict[str, str],
    index: BlockingIndex,
    max_candidates_per_s1: int = 15,
) -> Tuple[List[str], Dict[str, Set[str]]]:
    """Retrieve high-recall candidate set for a single Source 1 entity.

    Prioritizes exact name matches and falls back to token/prefix/address matching
    when additional candidates are needed.
    """
    s1_id = str(s1_row["entity_id"]).strip()
    norm_name = s1_row["norm_name"] if "norm_name" in s1_row and s1_row["norm_name"] else normalize_name(str(s1_row.get("business_name", "")))
    norm_addr = s1_row["norm_addr"] if "norm_addr" in s1_row and s1_row["norm_addr"] else normalize_address(str(s1_row.get("business_address", "")))
    norm_country = s1_row["norm_country"] if "norm_country" in s1_row and s1_row["norm_country"] else normalize_country(str(s1_row.get("country", "")))

    candidate_provenance: Dict[str, Set[str]] = defaultdict(set)
    candidate_scores: Dict[str, float] = defaultdict(float)

    # Rule 1: Exact normalized name match (Highest priority)
    if norm_name in index.exact_name_index:
        for cid in index.exact_name_index[norm_name]:
            if cid != s1_id and not cid.startswith("S1-"):
                candidate_provenance[cid].add("exact_name")
                candidate_scores[cid] += 10.0

    # Rule 2: Core name token overlap if more candidates needed
    if len(candidate_scores) < max_candidates_per_s1:
        core_tokens = get_core_name_tokens(norm_name)
        for token in core_tokens:
            if token in index.core_token_index:
                for cid in index.core_token_index[token]:
                    if cid != s1_id and not cid.startswith("S1-"):
                        candidate_provenance[cid].add(f"token_{token}")
                        candidate_scores[cid] += 2.0
                        if len(candidate_scores) >= max_candidates_per_s1 * 2:
                            break
            if len(candidate_scores) >= max_candidates_per_s1 * 2:
                break

    # Rule 3: Name prefix match if still below limit
    if len(candidate_scores) < max_candidates_per_s1 and norm_name and len(norm_name) >= 4:
        prefix = norm_name[:4]
        if prefix in index.prefix_index:
            for cid in index.prefix_index[prefix]:
                if cid != s1_id and not cid.startswith("S1-"):
                    candidate_provenance[cid].add("prefix_4")
                    candidate_scores[cid] += 1.0
                    if len(candidate_scores) >= max_candidates_per_s1 * 2:
                        break

    # Rule 4: Address numeric token + country match if still below limit
    if len(candidate_scores) < max_candidates_per_s1:
        numeric_tokens = extract_numeric_tokens(norm_addr)
        for num in numeric_tokens:
            key = (norm_country, num)
            if key in index.address_num_index:
                for cid in index.address_num_index[key]:
                    if cid != s1_id and not cid.startswith("S1-"):
                        candidate_provenance[cid].add("country_num")
                        candidate_scores[cid] += 1.5
                        if len(candidate_scores) >= max_candidates_per_s1 * 2:
                            break

    # Rank candidates by score descending
    ranked_candidates = sorted(
        candidate_scores.keys(),
        key=lambda c: candidate_scores[c],
        reverse=True,
    )

    final_candidates = ranked_candidates[:max_candidates_per_s1]
    return final_candidates, {c: candidate_provenance[c] for c in final_candidates}


def run_blocking_pipeline(
    source1_df: pd.DataFrame,
    pool_df: pd.DataFrame,
    max_candidates_per_s1: int = 15,
) -> Tuple[Dict[str, List[str]], Dict[Tuple[str, str], Set[str]], BlockingIndex]:
    """Execute blocking across all Source 1 entities against the target candidate pool."""
    index = BlockingIndex()
    index.build_from_dataframe(pool_df)

    candidate_map: Dict[str, List[str]] = {}
    pair_provenance: Dict[Tuple[str, str], Set[str]] = {}

    for _, row in source1_df.iterrows():
        s1_id = str(row["entity_id"]).strip()
        candidates, prov = retrieve_candidates_for_s1(
            s1_row=row.to_dict(),
            index=index,
            max_candidates_per_s1=max_candidates_per_s1,
        )
        candidate_map[s1_id] = candidates
        for cid, rules in prov.items():
            pair_provenance[(s1_id, cid)] = rules

    return candidate_map, pair_provenance, index
