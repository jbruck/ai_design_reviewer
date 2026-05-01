from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator


class ReviewPack(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    category: str
    prompts: list[str] = Field(min_length=1)

    @field_validator("id", "name", "category")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        if not value.strip():
            msg = "must not be blank"
            raise ValueError(msg)
        return value

    @field_validator("prompts")
    @classmethod
    def reject_blank_prompts(cls, prompts: list[str]) -> list[str]:
        for prompt in prompts:
            if not prompt.strip():
                msg = "prompts must not contain blank entries"
                raise ValueError(msg)
        return prompts


def load_review_pack(path: Path) -> ReviewPack:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return ReviewPack.model_validate(data)
    except (OSError, TypeError, yaml.YAMLError, ValidationError) as error:
        details = " ".join(str(error).splitlines())
        msg = f"Failed to load review pack {path}: {details}"
        raise ValueError(msg) from error


def load_review_packs(root: Path) -> list[ReviewPack]:
    packs_by_id: dict[str, tuple[ReviewPack, Path]] = {}
    for path in sorted(root.rglob("*.yaml")):
        pack = load_review_pack(path)
        if pack.id in packs_by_id:
            _, existing_path = packs_by_id[pack.id]
            msg = (
                f"Duplicate review pack id '{pack.id}' in {existing_path} and {path}."
            )
            raise ValueError(msg)
        packs_by_id[pack.id] = (pack, path)

    return [pack for pack, _ in sorted(packs_by_id.values(), key=lambda item: item[0].id)]
