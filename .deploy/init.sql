CREATE DATABASE IF NOT EXISTS `finbot`;
USE `finbot`;

CREATE TABLE IF NOT EXISTS `players` (
    `id` INT UNSIGNED AUTO_INCREMENT,
    `username` VARCHAR(255) NOT NULL UNIQUE,
    `fincount` INT NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `mapfins` (
    `mapname` VARCHAR(255) NOT NULL,
    `score` INT UNSIGNED NOT NULL,
    `rank` INT UNSIGNED NOT NULL,
    `date` TIMESTAMP NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `player_id` INT UNSIGNED NOT NULL,
    `score_delta` INT UNSIGNED DEFAULT 0,
    `rank_delta` INT DEFAULT 0,
    PRIMARY KEY(mapname, player_id),
    FOREIGN KEY (`player_id`) REFERENCES `players` (`id`)
    ON DELETE CASCADE
    ON UPDATE RESTRICT
) ENGINE = InnoDB;