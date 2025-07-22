-- MySQL dump 10.13  Distrib 8.0.41, for macos15 (arm64)
--
-- Host: 10.147.2.108    Database: order_service
-- ------------------------------------------------------
-- Server version	8.0.35-google

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `order_service`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `order_service` /*!40100 DEFAULT CHARACTER SET utf8mb3 */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `order_service`;

--
-- Table structure for table `kafka_events`
--

DROP TABLE IF EXISTS `kafka_events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `kafka_events` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `topic` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `partition_key` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT '',
  `data` mediumtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `iso_country_code` varchar(5) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'IN',
  UNIQUE KEY `idx` (`id`,`created_at`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=317996303 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `kafka_events_v2`
--

DROP TABLE IF EXISTS `kafka_events_v2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `kafka_events_v2` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `topic` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `partition_key` varchar(255) COLLATE utf8mb4_general_ci DEFAULT '',
  `data` text COLLATE utf8mb4_general_ci NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_general_ci NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `kafka_events_v3`
--

DROP TABLE IF EXISTS `kafka_events_v3`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `kafka_events_v3` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `topic` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `partition_key` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT '',
  `data` mediumtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `idx` (`id`,`created_at`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=208796 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
/*!50100 PARTITION BY RANGE (extract(year_month from `created_at`))
(PARTITION p_2409 VALUES LESS THAN (202410) ENGINE = InnoDB,
 PARTITION p_2410 VALUES LESS THAN (202411) ENGINE = InnoDB,
 PARTITION p_2411 VALUES LESS THAN (202412) ENGINE = InnoDB,
 PARTITION p_2412 VALUES LESS THAN (202501) ENGINE = InnoDB,
 PARTITION p_2501 VALUES LESS THAN (202502) ENGINE = InnoDB,
 PARTITION p_2502 VALUES LESS THAN (202503) ENGINE = InnoDB,
 PARTITION p_2503 VALUES LESS THAN (202504) ENGINE = InnoDB,
 PARTITION p_2504 VALUES LESS THAN (202505) ENGINE = InnoDB,
 PARTITION p_2505 VALUES LESS THAN (202506) ENGINE = InnoDB,
 PARTITION p_2506 VALUES LESS THAN (202507) ENGINE = InnoDB,
 PARTITION p_2507 VALUES LESS THAN (202508) ENGINE = InnoDB,
 PARTITION p_2508 VALUES LESS THAN (202509) ENGINE = InnoDB,
 PARTITION p_2509 VALUES LESS THAN (202510) ENGINE = InnoDB,
 PARTITION p_2510 VALUES LESS THAN (202511) ENGINE = InnoDB,
 PARTITION p_2511 VALUES LESS THAN (202512) ENGINE = InnoDB,
 PARTITION p_2512 VALUES LESS THAN (202601) ENGINE = InnoDB,
 PARTITION p_max VALUES LESS THAN MAXVALUE ENGINE = InnoDB) */;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `order_dead_jobs`
--

DROP TABLE IF EXISTS `order_dead_jobs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_dead_jobs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_num` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `type` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  `occurred_at` datetime DEFAULT NULL,
  `iso_country_code` varchar(3) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'IN',
  PRIMARY KEY (`id`),
  KEY `order_num_idx` (`order_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `order_events`
--

DROP TABLE IF EXISTS `order_events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_events` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `order_num` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` int NOT NULL,
  `type` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  `identifier` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  `source` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  `occurred_at` datetime NOT NULL,
  `record` json NOT NULL,
  `iso_country_code` varchar(3) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'IN',
  PRIMARY KEY (`id`,`occurred_at`),
  KEY `order_num_idx2` (`order_num`),
  KEY `identifier_idx2` (`identifier`),
  KEY `occ_idx2` (`occurred_at`)
) ENGINE=InnoDB AUTO_INCREMENT=10101882687 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `order_summary`
--

DROP TABLE IF EXISTS `order_summary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_summary` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `order_num` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` int NOT NULL,
  `order_id` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `iso_country_code` varchar(3) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'IN',
  PRIMARY KEY (`id`),
  UNIQUE KEY `order_num_idx` (`order_num`),
  KEY `user_id_idx` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3672407265 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `order_summary_mapping`
--

DROP TABLE IF EXISTS `order_summary_mapping`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_summary_mapping` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `order_summary_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `order_summary_id_idx` (`order_summary_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `supply_order_mapping`
--

DROP TABLE IF EXISTS `supply_order_mapping`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `supply_order_mapping` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `order_num` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sub_order_num` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` bigint NOT NULL,
  `order_summary_id` bigint NOT NULL,
  `supply_order_id` bigint DEFAULT NULL,
  `supply_order_detail_id` bigint DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `iso_country_code` varchar(3) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'IN',
  `split_order_num` varchar(25) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `order_num_idx` (`order_num`),
  KEY `order_summary_id_idx` (`order_summary_id`),
  KEY `split_order_num_idx` (`split_order_num`)
) ENGINE=InnoDB AUTO_INCREMENT=3645555885 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping events for database 'order_service'
--

--
-- Dumping routines for database 'order_service'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-07-10 16:53:52
