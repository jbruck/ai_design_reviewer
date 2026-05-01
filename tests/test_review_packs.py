from pathlib import Path

import pytest
import yaml

from dfm_reviewer.review_packs import ReviewPack, load_review_pack, load_review_packs


def test_load_review_pack_reads_yaml(tmp_path: Path) -> None:
    path = tmp_path / "machined.yaml"
    path.write_text(
        yaml.safe_dump(
            {
                "id": "machined",
                "name": "Machined Parts",
                "category": "manufacturing",
                "prompts": ["Check material callout.", "Check tolerances."],
            }
        ),
        encoding="utf-8",
    )

    pack = load_review_pack(path)

    assert isinstance(pack, ReviewPack)
    assert pack.id == "machined"
    assert pack.prompts == ["Check material callout.", "Check tolerances."]


def test_load_review_pack_rejects_missing_prompts_with_path_context(tmp_path: Path) -> None:
    path = tmp_path / "bad.yaml"
    path.write_text(
        "id: bad\nname: Bad Pack\ncategory: manufacturing\nprompt:\n  - Typo.\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match=r"bad\.yaml.*prompts"):
        load_review_pack(path)


def test_load_review_pack_rejects_blank_prompts(tmp_path: Path) -> None:
    path = tmp_path / "blank.yaml"
    path.write_text(
        "id: blank\nname: Blank Pack\ncategory: manufacturing\nprompts:\n  - '  '\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match=r"blank\.yaml.*blank"):
        load_review_pack(path)


def test_load_review_packs_finds_nested_yaml_files(tmp_path: Path) -> None:
    folder = tmp_path / "packs" / "manufacturing"
    folder.mkdir(parents=True)
    (folder / "machined.yaml").write_text(
        "id: machined\nname: Machined Parts\ncategory: manufacturing\nprompts:\n"
        "  - Check datum scheme.\n",
        encoding="utf-8",
    )

    packs = load_review_packs(tmp_path / "packs")

    assert [pack.id for pack in packs] == ["machined"]


def test_load_review_packs_rejects_duplicate_ids(tmp_path: Path) -> None:
    first = tmp_path / "packs" / "manufacturing" / "machined.yaml"
    second = tmp_path / "packs" / "iecex" / "machined.yaml"
    first.parent.mkdir(parents=True)
    second.parent.mkdir(parents=True)
    first.write_text(
        "id: machined\nname: Machined Parts\ncategory: manufacturing\nprompts:\n"
        "  - Check datum scheme.\n",
        encoding="utf-8",
    )
    second.write_text(
        "id: machined\nname: Duplicate Machined\ncategory: iecex\nprompts:\n"
        "  - Check duplicate behavior.\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Duplicate review pack id 'machined'.*machined.yaml"):
        load_review_packs(tmp_path / "packs")


def test_default_review_packs_cover_mvp_categories() -> None:
    packs = load_review_packs(Path("review_packs"))
    pack_ids = [pack.id for pack in packs]

    assert pack_ids == [
        "cable_electromechanical",
        "cast_moulded_encapsulated",
        "ex_d",
        "ex_e",
        "ex_i",
        "ex_m",
        "fabricated_welded",
        "machined",
        "manual_assembly",
        "simple_apparatus",
    ]
    assert {pack.category for pack in packs} == {"manufacturing", "iecex"}
    assert all(pack.prompts for pack in packs)
