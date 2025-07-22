CREATE TABLE `audience_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `audience_id` int NOT NULL,
  `name` varchar(128) NOT NULL,
  `description` text NOT NULL,
  `type` varchar(32) DEFAULT NULL,
  `refresh_query` text,
  `created_timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `aud_id` (`audience_id`),
  CONSTRAINT `audience_log_ibfk_1` FOREIGN KEY (`audience_id`) REFERENCES `audiences` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=26696 DEFAULT CHARSET=latin1;

Create Table: CREATE TABLE `kafka_events_v3` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `topic` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `partition_key` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '',
  `data` mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `iso_country_code` varchar(5) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'IN',
  PRIMARY KEY (`id`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=3079 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  
ALTER TABLE audiences ADD COLUMN created_timestamp timestamp NULL DEFAULT CURRENT_TIMESTAMP;
