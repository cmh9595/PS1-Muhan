# Cheap-Talk Audit

Same research question as the ACM proposal and the Hugging Face game.

## Shortest reproducible run

```bash
cd cheap-talk-audit
python -m unittest tests.test_cheap_talk -v
python -c "import sys; sys.path.insert(0,'src'); from cheap_talk import write_outputs; from pathlib import Path; write_outputs(Path('outputs'))"
```

Then open `notebooks/ps1_cheap_talk_audit.ipynb` and Run all (CPU, no API key).

`outputs/ps1_validation.json` stores the seed-206 totals, the $p^\star=0.6$ check, and the 1,000-seed means already obtained on 12 September 2026.

## Files

| Path | Role |
| --- | --- |
| `src/cheap_talk.py` | Portable session engine matching `hf_space/index.html` |
| `tests/test_cheap_talk.py` | Seed 206 and indifference assertions |
| `notebooks/ps1_cheap_talk_audit.ipynb` | Colab / local notebook |
| `hf_space/` | Static Space source (upload these files to Hugging Face) |
| `outputs/` | Saved synthetic results |

## Hugging Face

Upload `hf_space/index.html` and `hf_space/README.md` to [demo2](https://huggingface.co/spaces/dku-comsci-econ206-2026/demo2), or create a new Static Space and put that URL in the paper.

## License

MIT for original code in this folder.
