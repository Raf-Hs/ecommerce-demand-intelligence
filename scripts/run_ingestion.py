"""Run all available ingestions."""

from src.ingestion.hm_sample import ingest_hm_sample
from src.ingestion.uci import ingest_uci
from src.utils.logging import get_logger

log = get_logger("run_ingestion")


def main() -> None:
    paths = []
    paths += ingest_hm_sample()
    paths += ingest_uci()
    log.info("ingestion_run_complete", files_written=len(paths))
    for p in paths:
        print(p)


if __name__ == "__main__":
    main()
