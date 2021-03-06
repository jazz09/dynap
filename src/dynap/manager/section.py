from __future__ import absolute_import, annotations

import logging
from dynap.dao.collector import DaoCollector
from dynap.dao.common import DaoEntryNotFound
from dynap.model.job import DeployedJob, Stream

logger = logging.getLogger("dynap.manager.section")


class CriticalSectionManager:

    def __init__(self, dao_collector: DaoCollector):
        self._dao_collector = dao_collector

    @staticmethod
    def get_associated_job(daocollector: DaoCollector, topic: str, job_name: str) -> DeployedJob:
        deployed_jobs = daocollector.job_dao.list()
        upstream = Stream(
            address="localhost",
            topic="topic1",
            sequence_number=0,
            requesting_cs=False
        )
        downstream = Stream(
            address="localhost",
            topic="topic1",
            sequence_number=0,
            requesting_cs=False
        )
        job = DeployedJob(
            job_name="test_job",
            agent_address="localhost",
            upstream=[upstream],
            downstream=[downstream],
            entry_class="test.package.class",
            jar_id="x",
            job_id="y",
            jar_name="test_jar_name",
            sequence_number=0,
            requesting_cs=False
        )
        for deployed_job in deployed_jobs:
            for upstream in deployed_job.upstream:
                if upstream.topic == topic and deployed_job.job_name != job_name:
                    job = deployed_job
            for downstream in deployed_job.downstream:
                if downstream.topic == topic and deployed_job.job_name != job_name:
                    job = deployed_job
        logger.info(f"Returning assiciated job.")
        return job

    @staticmethod
    def check_job_exist(daocollector: DaoCollector, job_id: str) -> bool:
        running = True
        try:
            daocollector.job_dao.get(job_id)
        except DaoEntryNotFound:
            running = False
        # daocollector.job_dao.get(job_id)
        # if DaoEntryNotFound:
        #     running = False
        logger.info(f"Returning jobid exist, running is {running}")
        return running

    @staticmethod
    def check_job_request_status(daocollector: DaoCollector, job_id: str) -> bool:
        try:
            deployed_job = daocollector.job_dao.get(job_id)
            if deployed_job.requesting_cs:
                requesting = True
            else:
                requesting = False
        except DaoEntryNotFound:
            requesting = False
        logger.info(f"Returning jobid {job_id} exist, requesting is {requesting}")
        return requesting

    @staticmethod
    def get_max_sequence_number(daocollector: DaoCollector, job_name: str) -> int:
        sequence_numbers = []
        deployed_jobs = daocollector.job_dao.list()
        for deployed_job in deployed_jobs:
            if deployed_job.job_name == job_name:
                for upstream in deployed_job.upstream:
                    sequence_numbers.append(upstream.sequence_number)
                for downstream in deployed_job.downstream:
                    sequence_numbers.append(downstream.sequence_number)
                sequence_numbers.append(deployed_job.sequence_number)
        return max(sequence_numbers)

    @staticmethod
    def update_sequence_number(daocollector: DaoCollector, job_id: str, topic: str, sequence_number: int):
        deployed_job = daocollector.job_dao.get(job_id)
        for downstream in deployed_job.downstream:
            if downstream.topic == topic:
                downstream.sequence_number = sequence_number
                logger.info(f"Updated the DS topic {topic}, with sequence number {sequence_number}")
        for upstream in deployed_job.upstream:
            if upstream.topic == topic:
                upstream.sequence_number = sequence_number
                logger.info(f"Updated the US topic {topic}, with sequence number {sequence_number}")
        daocollector.job_dao.update(deployed_job)
