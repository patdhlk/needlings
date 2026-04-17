from pathlib import Path

from needlings.compose import compose_build_dir


def test_compose_merges_base_and_starter(tmp_path: Path) -> None:
    base = tmp_path / "_base"
    base.mkdir()
    (base / "conf.py").write_text("# base conf\n")
    (base / "index.rst").write_text(".. toctree::\n")

    starter = tmp_path / "starter"
    starter.mkdir()
    (starter / "index.rst").write_text(".. I AM NOT DONE\n")  # overrides base index

    out = tmp_path / "out"
    compose_build_dir(base=base, starter=starter, out=out)

    assert (out / "conf.py").read_text() == "# base conf\n"
    assert (out / "index.rst").read_text() == ".. I AM NOT DONE\n"


def test_compose_overrides_base_files_with_starter(tmp_path: Path) -> None:
    base = tmp_path / "_base"
    base.mkdir()
    (base / "ubproject.toml").write_text('# base\n')
    starter = tmp_path / "starter"
    starter.mkdir()
    (starter / "ubproject.toml").write_text('# exercise-specific\n')

    out = tmp_path / "out"
    compose_build_dir(base=base, starter=starter, out=out)

    assert (out / "ubproject.toml").read_text() == "# exercise-specific\n"


def test_compose_handles_nested_dirs(tmp_path: Path) -> None:
    base = tmp_path / "_base"
    (base / "features").mkdir(parents=True)
    (base / "features" / "a.rst").write_text("A\n")

    starter = tmp_path / "starter"
    (starter / "features").mkdir(parents=True)
    (starter / "features" / "b.rst").write_text("B\n")

    out = tmp_path / "out"
    compose_build_dir(base=base, starter=starter, out=out)

    assert (out / "features" / "a.rst").read_text() == "A\n"
    assert (out / "features" / "b.rst").read_text() == "B\n"


def test_compose_wipes_existing_out(tmp_path: Path) -> None:
    base = tmp_path / "_base"
    base.mkdir()
    (base / "conf.py").write_text("x\n")
    starter = tmp_path / "starter"
    starter.mkdir()

    out = tmp_path / "out"
    out.mkdir()
    (out / "stale.txt").write_text("stale\n")

    compose_build_dir(base=base, starter=starter, out=out)
    assert not (out / "stale.txt").exists()
