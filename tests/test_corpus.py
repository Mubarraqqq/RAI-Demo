import json
import tempfile
import unittest
from pathlib import Path

from build_corpus import build_chunk_records, build_documents, load_registry, write_jsonl
from storage import Storage


class CorpusBuildTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry_path = Path("data/processed/corpus_registry.json")
        self.registry = load_registry(self.registry_path)

    def test_registry_contains_all_subfacets(self) -> None:
        self.assertEqual(len(self.registry["subfacets"]), 31)

    def test_registry_tracks_known_missing_worksheet_subfacets(self) -> None:
        missing = sorted(
            item["canonical_name"]
            for item in self.registry["subfacets"]
            if not item["worksheet_assets"]
        )
        self.assertEqual(
            missing,
            ["Identifying a mentor or coach", "People you can confide in"],
        )

    def test_build_documents_from_small_registry_slice(self) -> None:
        sample_registry = {
            **self.registry,
            "subfacets": self.registry["subfacets"][:1],
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "documents.jsonl"
            module_cache = Path(tmpdir) / ".swift-module-cache"
            doc_count, failure_count = build_documents(
                registry=sample_registry,
                output_path=output_path,
                module_cache=module_cache,
            )

            self.assertEqual(failure_count, 0)
            self.assertEqual(doc_count, 2)
            self.assertTrue(output_path.exists())

            records = [
                json.loads(line)
                for line in output_path.read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(records[0]["subfacet_id"], "adapting-to-change")
            self.assertIn(records[0]["asset_type"], {"slides", "worksheets"})

    def test_storage_can_load_built_documents(self) -> None:
        sample_registry = {
            **self.registry,
            "subfacets": self.registry["subfacets"][:1],
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "documents.jsonl"
            module_cache = Path(tmpdir) / ".swift-module-cache"
            db_path = Path(tmpdir) / "manifest.db"

            build_documents(
                registry=sample_registry,
                output_path=output_path,
                module_cache=module_cache,
            )

            store = Storage(str(db_path))
            store.initialize()
            inserted = store.load_documents(str(output_path))
            documents = [
                json.loads(line)
                for line in output_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            chunks = build_chunk_records(documents)
            chunks_path = Path(tmpdir) / "chunks.jsonl"
            write_jsonl(chunks_path, chunks)
            chunk_inserted = store.load_chunks(str(chunks_path))

            self.assertEqual(inserted, 2)
            self.assertGreater(chunk_inserted, 2)
            assets = store.list_assets_for_subfacet("adapting-to-change")
            self.assertEqual(len(assets), 2)
            self.assertEqual(assets[0]["subfacet_id"], "adapting-to-change")

    def test_embedding_search_ranks_closest_vector_within_subfacet(self) -> None:
        sample_registry = {
            **self.registry,
            "subfacets": self.registry["subfacets"][:1],
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            output_path = tmp_path / "documents.jsonl"
            chunks_path = tmp_path / "chunks.jsonl"
            embeddings_path = tmp_path / "embeddings.jsonl"
            db_path = tmp_path / "manifest.db"

            build_documents(
                registry=sample_registry,
                output_path=output_path,
                module_cache=tmp_path / ".swift-module-cache",
            )
            documents = [
                json.loads(line)
                for line in output_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            chunks = build_chunk_records(documents)[:2]
            write_jsonl(chunks_path, chunks)
            write_jsonl(
                embeddings_path,
                [
                    {
                        "chunk_id": chunks[0]["chunk_id"],
                        "model": "text-embedding-3-small",
                        "embedding": [1.0, 0.0],
                    },
                    {
                        "chunk_id": chunks[1]["chunk_id"],
                        "model": "text-embedding-3-small",
                        "embedding": [0.0, 1.0],
                    },
                ],
            )

            store = Storage(str(db_path))
            store.initialize()
            store.load_documents(str(output_path))
            store.load_chunks(str(chunks_path))
            store.load_embeddings(str(embeddings_path))

            results = store.search_embedding_chunks(
                "adapting-to-change",
                query_embedding=[0.9, 0.1],
                limit=1,
            )

            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["chunk_id"], chunks[0]["chunk_id"])
            self.assertEqual(results[0]["retrieval"], "embedding")


if __name__ == "__main__":
    unittest.main()
