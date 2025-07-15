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

ALTER TABLE audiences ADD COLUMN created_timestamp timestamp NULL DEFAULT CURRENT_TIMESTAMP;
