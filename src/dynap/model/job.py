from __future__ import absolute_import, annotations
from dataclasses import dataclass

import logging
from typing import List

logger = logging.getLogger("dynap.model.job")


@dataclass
class Stream:
    address: str
    topic: str
    sequence_number: int = 0
    requesting_cs: bool = False

    def to_repr(self) -> dict:
        return {
            "address": self.address,
            "topic": self.topic,
            "sequence_number": self.sequence_number,
            "requesting_cs": self.requesting_cs
        }

    @staticmethod
    def from_repr(raw_data: dict) -> Stream:
        return Stream(
            address=raw_data["address"],
            topic=raw_data["topic"],
            sequence_number=raw_data["sequence_number"],
            requesting_cs=raw_data["requesting_cs"]
        )


@dataclass
class Job:
    job_name: str
    agent_address: str
    upstream: List[Stream]
    downstream: List[Stream]
    entry_class: str
    sequence_number: int

    def to_repr(self) -> dict:
        job = {
            "job_name": self.job_name,
            "agent_address": self.agent_address,
            "upstream": [],
            "downstream": [],
            "entry_class": self.entry_class,
            "sequence_number": self.sequence_number
        }
        for x in self.upstream:
            job["upstream"].append(x.to_repr())
        for y in self.downstream:
            job["downstream"].append(y.to_repr())
        return job

    @staticmethod
    def from_repr(raw_data: dict) -> Job:
        upstream = []
        for raw_entry in raw_data["upstream"]:
            upstream.append(Stream.from_repr(raw_entry))
        downstream = []
        for raw_entry in raw_data["downstream"]:
            downstream.append(Stream.from_repr(raw_entry))
        return Job(
            job_name=raw_data["job_name"],
            agent_address=raw_data["agent_address"],
            upstream=upstream,
            downstream=downstream,
            entry_class=raw_data["entry_class"],
            sequence_number=raw_data["sequence_number"],
        )


@dataclass
class DeployedJob(Job):

    jar_id: str
    job_id: str
    jar_name: str
    requesting_cs: bool = False

    def to_repr(self) -> dict:
        job = super().to_repr()
        job["jar_id"] = self.jar_id
        job["job_id"] = self.job_id
        job["jar_name"] = self.jar_name
        job["requesting_cs"] = self.requesting_cs
        return job

    @staticmethod
    def from_repr(raw_data: dict) -> DeployedJob:
        job = Job.from_repr(raw_data)
        return DeployedJob(
            job_name=job.job_name,
            agent_address=job.agent_address,
            upstream=job.upstream,
            downstream=job.downstream,
            entry_class=job.entry_class,
            sequence_number=job.sequence_number,
            jar_id=raw_data["jar_id"],
            job_id=raw_data["job_id"],
            jar_name=raw_data["jar_name"],
            requesting_cs=raw_data["requesting_cs"]
        )
