-- MySQL dump 10.13  Distrib 8.0.41, for macos15 (arm64)
--
-- Host: 172.23.252.113    Database: ab
-- ------------------------------------------------------
-- Server version	8.0.32-google

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
-- Current Database: `ab`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `ab` /*!40100 DEFAULT CHARACTER SET latin1 */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `ab`;

--
-- Table structure for table `audience_change_log`
--

DROP TABLE IF EXISTS `audience_change_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `audience_change_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `audience_id` int NOT NULL,
  `name` varchar(128) NOT NULL,
  `description` text NOT NULL,
  `type` varchar(32) DEFAULT NULL,
  `refresh_query` text,
  `refresh_query_type` varchar(20) DEFAULT 'REDSHIFT',
  `refresh_frequency` int DEFAULT NULL,
  `country` varchar(5) NOT NULL,
  `entity_type` varchar(100) DEFAULT NULL,
  `modified_by` varchar(64) NOT NULL,
  `created_timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `aud_id` (`audience_id`),
  CONSTRAINT `audience_change_log_ibfk_1` FOREIGN KEY (`audience_id`) REFERENCES `audiences` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=26696 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `audience_lock`
--

DROP TABLE IF EXISTS `audience_lock`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `audience_lock` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `audience_id` int unsigned NOT NULL,
  `locked_for` varchar(50) DEFAULT NULL,
  `locked_by` varchar(50) DEFAULT NULL,
  `locked_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_lock` (`audience_id`,`locked_for`)
) ENGINE=InnoDB AUTO_INCREMENT=249146 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `audience_refresh_stages`
--

DROP TABLE IF EXISTS `audience_refresh_stages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `audience_refresh_stages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `audience_id` int NOT NULL,
  `refresh_stage` int DEFAULT '0',
  `updated_timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `aud_refresh_id` (`audience_id`),
  CONSTRAINT `audience_refresh_log_ibfk_1` FOREIGN KEY (`audience_id`) REFERENCES `audiences` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=102356353 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `audience_renewal`
--

DROP TABLE IF EXISTS `audience_renewal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `audience_renewal` (
  `audience_id` int NOT NULL,
  `renewal_status` enum('STOPPED','RENEWED','EXPIRED','PENDING') NOT NULL,
  `expiry_date_timestamp` timestamp NOT NULL,
  `renewed_by` varchar(64) NOT NULL,
  `renewed_count` int NOT NULL,
  `watchers_list` varchar(512) NOT NULL,
  `renewal_freq_days` int NOT NULL,
  `created_timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`audience_id`),
  CONSTRAINT `audience_renewal_ibfk_1` FOREIGN KEY (`audience_id`) REFERENCES `audiences` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `audience_renewal_change_log`
--

DROP TABLE IF EXISTS `audience_renewal_change_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `audience_renewal_change_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `audience_id` int NOT NULL,
  `renewal_status` enum('STOPPED','RENEWED','EXPIRED','PENDING') NOT NULL,
  `renewed_timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `renewed_by` varchar(64) NOT NULL,
  `renewed_count` int NOT NULL,
  `watchers_list` varchar(512) NOT NULL,
  `renewal_freq_days` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `aud_ren_id` (`audience_id`),
  CONSTRAINT `audience_renewal_change_log_ibfk_1` FOREIGN KEY (`audience_id`) REFERENCES `audience_renewal` (`audience_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=28367 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `audience_types`
--

DROP TABLE IF EXISTS `audience_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `audience_types` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `audience_type` varchar(255) NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `audiences`
--

DROP TABLE IF EXISTS `audiences`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `audiences` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL DEFAULT '',
  `description` text NOT NULL,
  `type` varchar(32) NOT NULL,
  `active` tinyint(1) NOT NULL DEFAULT '0' COMMENT '0 = Will be picked up in next refresh cycle, 1=will be picked up if past last refresh_time and refresh rfeq construct, -1=In processing queue, 2=will not be refreshed',
  `created_by` varchar(64) DEFAULT NULL,
  `count` int DEFAULT NULL,
  `refresh_query` text,
  `refresh_frequency` int DEFAULT NULL,
  `refresh_timestamp` timestamp NULL DEFAULT NULL,
  `created_timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `country` varchar(5) NOT NULL DEFAULT 'IN',
  `entity_type` varchar(32) NOT NULL DEFAULT 'RESELLER',
  `refresh_query_type` varchar(20) DEFAULT 'REDSHIFT',
  `purged` int DEFAULT '0',
  `audience_refresh_stage` int DEFAULT NULL,
  `audience_refresh_stage_timestamp` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `aud_type` (`type`),
  KEY `ref_freq` (`refresh_frequency`),
  KEY `aud_rf_ts` (`refresh_timestamp`),
  KEY `aud_create_time` (`created_timestamp`),
  KEY `aud_create_by` (`created_by`),
  KEY `aud_active` (`active`),
  KEY `country` (`country`)
) ENGINE=InnoDB AUTO_INCREMENT=117391 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `bucket_reserve_logs`
--

DROP TABLE IF EXISTS `bucket_reserve_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bucket_reserve_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `team_id` int DEFAULT NULL,
  `plane_id` int DEFAULT NULL,
  `entity_type` varchar(100) DEFAULT NULL,
  `sample_size` int DEFAULT NULL,
  `variants_count` int DEFAULT NULL,
  `start_time` int DEFAULT NULL,
  `end_time` int DEFAULT NULL,
  `buckets` text,
  `experiment_id` int DEFAULT NULL,
  `reserve_status` varchar(100) DEFAULT NULL,
  `updated_timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2418 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `experiment_audiences_map`
--

DROP TABLE IF EXISTS `experiment_audiences_map`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `experiment_audiences_map` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `experiment_id` int NOT NULL,
  `audience_id` int NOT NULL,
  `anonymous_audience_id` int NOT NULL,
  `created_timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `country` varchar(5) NOT NULL DEFAULT 'IN',
  PRIMARY KEY (`id`),
  KEY `exp_id` (`experiment_id`),
  KEY `aud_id` (`audience_id`),
  KEY `anon_aud_id` (`anonymous_audience_id`),
  KEY `exp_aud_create_time` (`created_timestamp`),
  CONSTRAINT `experiment_audiences_map_ibfk_1` FOREIGN KEY (`experiment_id`) REFERENCES `experiments` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=2984 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `experiment_buckets_map`
--

DROP TABLE IF EXISTS `experiment_buckets_map`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `experiment_buckets_map` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `plane_id` int NOT NULL,
  `bucket_id` smallint unsigned NOT NULL,
  `experiment_id` int NOT NULL,
  `active` tinyint(1) NOT NULL,
  `created_timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `country` varchar(5) NOT NULL DEFAULT 'IN',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=128888 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `experiment_references_map`
--

DROP TABLE IF EXISTS `experiment_references_map`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `experiment_references_map` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `experiment_id` int NOT NULL,
  `reference` varchar(100) NOT NULL,
  `created_timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `country` varchar(5) NOT NULL DEFAULT 'IN',
  PRIMARY KEY (`id`),
  UNIQUE KEY `experiment_reference_key` (`experiment_id`,`reference`),
  KEY `referenceKey` (`reference`),
  KEY `exp_ref_create_time` (`created_timestamp`),
  CONSTRAINT `experiment_references_map_ibfk_1` FOREIGN KEY (`experiment_id`) REFERENCES `experiments` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=13818407 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `experiments`
--

DROP TABLE IF EXISTS `experiments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `experiments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(256) NOT NULL,
  `type` varchar(128) NOT NULL DEFAULT '',
  `valid` tinyint(1) NOT NULL,
  `reference_check` tinyint(1) NOT NULL DEFAULT '0',
  `created_by` varchar(64) DEFAULT NULL,
  `start_time` int DEFAULT NULL,
  `end_time` int DEFAULT NULL,
  `created_timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `country` varchar(5) NOT NULL DEFAULT 'IN',
  `entity_type` varchar(32) NOT NULL DEFAULT 'RESELLER',
  `problem_statement` text,
  `hypotheses` text,
  `reference_doc` text,
  `status` varchar(50) NOT NULL DEFAULT 'SAMPLE_SIZE_CALCULATION_PENDING',
  `filter_query` text,
  `collaborators` varchar(512) DEFAULT NULL,
  `refresh_audience` int DEFAULT '0',
  `team_id` int NOT NULL DEFAULT '1',
  `plane_id` int DEFAULT NULL,
  `version` varchar(20) NOT NULL DEFAULT 'OLD',
  `sensitivity` double DEFAULT NULL,
  `north_star_metric` varchar(100) DEFAULT NULL,
  `check_metrics` text,
  `north_star_impact` text,
  `real_estate_impacting` text,
  `sample_size` bigint DEFAULT NULL,
  `variance` double DEFAULT NULL,
  `metric_dashboard` text,
  `last_bucket_variant_sync_ts_millis` mediumtext,
  `buckets` varchar(4000) DEFAULT NULL,
  `entity_variant_assignment_seed` int DEFAULT NULL,
  `feature_name` text,
  `refresh_frequency` int DEFAULT NULL,
  `minimum_bucket_count` bigint DEFAULT NULL,
  `mau` bigint DEFAULT NULL,
  `dau` bigint DEFAULT NULL,
  `users_per_bucket_count` bigint DEFAULT NULL,
  `mean` double DEFAULT NULL,
  `mde` double DEFAULT NULL,
  `latest_audience_refresh_status` varchar(50) DEFAULT NULL,
  `last_successful_audience_refresh_ts_millis` bigint DEFAULT '0',
  `stage` varchar(100) DEFAULT NULL,
  `metadata` text,
  `segment_name` varchar(200) DEFAULT NULL,
  `exposure_percent` double DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `exp_type` (`type`),
  KEY `exp_valid` (`valid`),
  KEY `exp_end_time` (`end_time`),
  KEY `exp_create_time` (`created_timestamp`),
  KEY `exp_ref` (`reference_check`),
  KEY `exp_start_time` (`start_time`),
  KEY `country` (`country`),
  KEY `exp_entity_type` (`entity_type`)
) ENGINE=InnoDB AUTO_INCREMENT=3082 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `faq_level_1`
--

DROP TABLE IF EXISTS `faq_level_1`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `faq_level_1` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `slug` varchar(256) DEFAULT NULL,
  `image_id` int DEFAULT NULL,
  `valid` tinyint DEFAULT '1',
  `priority` int DEFAULT '1',
  `created` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `faq_level_3_content`
--

DROP TABLE IF EXISTS `faq_level_3_content`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `faq_level_3_content` (
  `id` int NOT NULL AUTO_INCREMENT,
  `faq_level_3_id` int NOT NULL,
  `language_id` int NOT NULL,
  `title` varchar(500) NOT NULL,
  `details` text,
  `object_id` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=203 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `homogeneity_check_stats`
--

DROP TABLE IF EXISTS `homogeneity_check_stats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `homogeneity_check_stats` (
  `id` int NOT NULL AUTO_INCREMENT,
  `experiment_id` int NOT NULL,
  `control_audience_id` int NOT NULL,
  `variant_audience_id` int NOT NULL,
  `status` varchar(100) DEFAULT NULL,
  `p_value` double DEFAULT NULL,
  `request_id` int DEFAULT NULL,
  `created_timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `t_value` double DEFAULT NULL,
  `df_value` double DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=303 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `images`
--

DROP TABLE IF EXISTS `images`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `images` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `filename` varchar(256) DEFAULT '',
  `path` text,
  `originalname` text,
  `size` int DEFAULT NULL,
  `mimetype` varchar(256) DEFAULT NULL,
  `height` int DEFAULT NULL,
  `width` int DEFAULT NULL,
  `valid` tinyint DEFAULT '1',
  `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `name` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `locked_plane_ids`
--

DROP TABLE IF EXISTS `locked_plane_ids`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `locked_plane_ids` (
  `id` int NOT NULL AUTO_INCREMENT,
  `plane_id` int NOT NULL,
  `attempts` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `plane_id` (`plane_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `membership_faq_level_3`
--

DROP TABLE IF EXISTS `membership_faq_level_3`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `membership_faq_level_3` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `slug` varchar(512) DEFAULT NULL,
  `faq_level_2_id` int DEFAULT NULL,
  `likes` int DEFAULT '0',
  `dislikes` int DEFAULT '0',
  `priority` int DEFAULT NULL,
  `commonly_asked` tinyint DEFAULT NULL,
  `commonly_asked_priority` int DEFAULT NULL,
  `meta_title` varchar(512) DEFAULT NULL,
  `meta_keywords` text,
  `meta_description` text,
  `author` int DEFAULT NULL,
  `valid` tinyint DEFAULT '1',
  `draft` tinyint DEFAULT '0',
  `published` tinyint DEFAULT '0',
  `published_at` timestamp NULL DEFAULT NULL,
  `created` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `membership_faq_level_3_content`
--

DROP TABLE IF EXISTS `membership_faq_level_3_content`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `membership_faq_level_3_content` (
  `id` int NOT NULL AUTO_INCREMENT,
  `faq_level_3_id` int NOT NULL,
  `language_id` int NOT NULL,
  `title` varchar(500) NOT NULL,
  `details` text,
  `object_id` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `membership_user_like_map`
--

DROP TABLE IF EXISTS `membership_user_like_map`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `membership_user_like_map` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `faq_level_3_id` int NOT NULL,
  `type` int NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4464 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `plane_change_log`
--

DROP TABLE IF EXISTS `plane_change_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `plane_change_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `plane_id` int NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `description` varchar(1000) DEFAULT NULL,
  `buckets_status` varchar(1010) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `modified_by` varchar(100) DEFAULT NULL,
  `created_timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `total_buckets_count` int DEFAULT NULL,
  `available_buckets_count` int DEFAULT NULL,
  `control_buckets_count` int DEFAULT NULL,
  `entity_types` varchar(100) DEFAULT NULL,
  `entity_bucket_assignment_seed` int DEFAULT NULL,
  `is_overlapping_experiment_plane` tinyint(1) NOT NULL DEFAULT '0',
  `type` varchar(20) NOT NULL,
  `config` text,
  `is_root` tinyint NOT NULL DEFAULT '0',
  `plane_entity_assignment_checkpoint_millis` bigint DEFAULT NULL,
  `version` int DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=60 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `planes`
--

DROP TABLE IF EXISTS `planes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `planes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `description` varchar(1000) DEFAULT NULL,
  `buckets_status` varchar(1010) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `created_by` varchar(100) DEFAULT NULL,
  `created_timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `total_buckets_count` int DEFAULT NULL,
  `available_buckets_count` int DEFAULT NULL,
  `control_buckets_count` int DEFAULT NULL,
  `entity_types` varchar(100) NOT NULL,
  `entity_bucket_assignment_seed` int NOT NULL,
  `is_overlapping_experiment_plane` tinyint(1) NOT NULL DEFAULT '0',
  `type` varchar(20) NOT NULL,
  `config` text,
  `is_root` tinyint NOT NULL DEFAULT '0',
  `plane_entity_assignment_checkpoint_millis` bigint DEFAULT NULL,
  `version` int DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=144 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `real_estates`
--

DROP TABLE IF EXISTS `real_estates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `real_estates` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `created_timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `code` varchar(30) DEFAULT NULL,
  `active` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `reseller_anonymous_planes_map`
--

DROP TABLE IF EXISTS `reseller_anonymous_planes_map`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reseller_anonymous_planes_map` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `reseller_plane_id` int NOT NULL,
  `anonymous_plane_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `const_two` (`anonymous_plane_id`),
  KEY `reseller_plane` (`reseller_plane_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `teams`
--

DROP TABLE IF EXISTS `teams`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `teams` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `description` varchar(1000) DEFAULT NULL,
  `team_group_email` varchar(100) NOT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `created_by` varchar(100) DEFAULT NULL,
  `created_timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `ui_configs` varchar(1000) DEFAULT '{"is_visible":true,"is_filterable":true}',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `teams_planes_map`
--

DROP TABLE IF EXISTS `teams_planes_map`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `teams_planes_map` (
  `id` int NOT NULL AUTO_INCREMENT,
  `team_id` int NOT NULL,
  `plane_id` int NOT NULL,
  `created_timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `active` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=356 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_language_map`
--

DROP TABLE IF EXISTS `user_language_map`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_language_map` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `language_id` int NOT NULL,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3148313 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_like_map`
--

DROP TABLE IF EXISTS `user_like_map`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_like_map` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `faq_level_3_id` int NOT NULL,
  `type` int NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `faq_level_3_id` (`faq_level_3_id`),
  KEY `user_id` (`user_id`),
  KEY `type` (`type`)
) ENGINE=InnoDB AUTO_INCREMENT=207550 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(256) DEFAULT NULL,
  `email` varchar(256) DEFAULT NULL,
  `password` varchar(256) DEFAULT NULL,
  `valid` tinyint DEFAULT '1',
  `created` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `variants`
--

DROP TABLE IF EXISTS `variants`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `variants` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL DEFAULT '',
  `experiment_id` int NOT NULL,
  `audience` varchar(32) NOT NULL,
  `configuration` text CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci,
  `created_timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `country` varchar(5) NOT NULL DEFAULT 'IN',
  `description` text,
  `is_control` int DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `variant_experiment_key` (`id`,`experiment_id`),
  KEY `experiment_id` (`experiment_id`)
) ENGINE=InnoDB AUTO_INCREMENT=19377 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `variants_deleted`
--

DROP TABLE IF EXISTS `variants_deleted`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `variants_deleted` (
  `id` int NOT NULL,
  `name` varchar(128) NOT NULL DEFAULT '',
  `experiment_id` int NOT NULL,
  `audience` varchar(32) NOT NULL,
  `configuration` text CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci,
  `created_timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `country` varchar(5) NOT NULL DEFAULT 'IN',
  `description` text,
  `is_control` int DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `variant_experiment_key` (`id`,`experiment_id`),
  KEY `experiment_id` (`experiment_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `video_audience_map`
--

DROP TABLE IF EXISTS `video_audience_map`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `video_audience_map` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `video_id` int NOT NULL,
  `audience_id` int NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `video_language_map`
--

DROP TABLE IF EXISTS `video_language_map`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `video_language_map` (
  `id` int NOT NULL AUTO_INCREMENT,
  `video_id` int NOT NULL,
  `language_id` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `videos`
--

DROP TABLE IF EXISTS `videos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `videos` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `heading` varchar(256) DEFAULT NULL,
  `type` varchar(256) DEFAULT NULL,
  `image_id` int DEFAULT NULL,
  `category_id` int DEFAULT NULL,
  `video_url` varchar(512) DEFAULT NULL,
  `priority` int DEFAULT '1',
  `show_home` tinyint DEFAULT NULL,
  `home_page_priority` int DEFAULT NULL,
  `valid` tinyint DEFAULT '1',
  `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping events for database 'ab'
--

--
-- Dumping routines for database 'ab'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-07-10 15:27:20
