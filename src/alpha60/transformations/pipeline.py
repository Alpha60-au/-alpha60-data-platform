"""Transformation pipeline orchestration."""

from collections.abc import Callable
from dataclasses import dataclass

from alpha60.config.settings import Settings
from alpha60.transformations.result import TransformationResult, TransformationStatus


TransformationCallable = Callable[..., TransformationResult]


@dataclass(frozen=True, slots=True)
class TransformationPipelineStep:
    """A single transformation pipeline step."""

    name: str
    run: TransformationCallable


@dataclass(frozen=True, slots=True)
class TransformationPipelineResult:
    """Result from running a transformation pipeline."""

    status: TransformationStatus
    results: list[TransformationResult]


class TransformationPipeline:
    """Run transformations in dependency order."""

    def __init__(self, steps: list[TransformationPipelineStep]) -> None:
        """Create a transformation pipeline."""
        self._steps = steps

    def run(
        self,
        settings: Settings,
        staging_dataset_id: str | None = None,
    ) -> TransformationPipelineResult:
        """Run every transformation step until one fails."""
        results: list[TransformationResult] = []

        resolved_staging_dataset_id = (
            staging_dataset_id or settings.bigquery.staging_dataset_id
        )

        for step in self._steps:
            result = step.run(
                settings=settings,
                staging_dataset_id=resolved_staging_dataset_id,
            )
            results.append(result)

            if result.status != TransformationStatus.SUCCESS:
                return TransformationPipelineResult(
                    status=TransformationStatus.FAILED,
                    results=results,
                )

        return TransformationPipelineResult(
            status=TransformationStatus.SUCCESS,
            results=results,
        )
