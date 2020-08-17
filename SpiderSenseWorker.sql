/*
 Navicat Premium Data Transfer

 Source Server         : localhost_3306
 Source Server Type    : MySQL
 Source Server Version : 80021
 Source Host           : 127.0.0.1:3306
 Source Schema         : SpiderSenseWorker

 Target Server Type    : MySQL
 Target Server Version : 80021
 File Encoding         : 65001

 Date: 17/08/2020 11:42:13
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for build
-- ----------------------------
DROP TABLE IF EXISTS `build`;
CREATE TABLE `build` (
  `buildId` int NOT NULL AUTO_INCREMENT,
  `projectId` int DEFAULT NULL,
  `commitId` varchar(255) DEFAULT NULL,
  `message` varchar(255) DEFAULT NULL,
  `committer` varchar(255) DEFAULT NULL,
  `timestamp` double DEFAULT NULL,
  PRIMARY KEY (`buildId`),
  KEY `proj_fr` (`projectId`),
  CONSTRAINT `proj_fr` FOREIGN KEY (`projectId`) REFERENCES `project` (`projectId`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Table structure for coverage
-- ----------------------------
DROP TABLE IF EXISTS `coverage`;
CREATE TABLE `coverage` (
  `lineId` int NOT NULL,
  `testcaseId` int NOT NULL,
  PRIMARY KEY (`lineId`,`testcaseId`),
  KEY `coverage_ibfk_2` (`testcaseId`),
  CONSTRAINT `coverage_ibfk_1` FOREIGN KEY (`lineId`) REFERENCES `line` (`lineId`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `coverage_ibfk_2` FOREIGN KEY (`testcaseId`) REFERENCES `testcase` (`testcaseId`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Table structure for line
-- ----------------------------
DROP TABLE IF EXISTS `line`;
CREATE TABLE `line` (
  `lineId` int NOT NULL AUTO_INCREMENT,
  `projectId` int DEFAULT NULL,
  `buildId` int DEFAULT NULL,
  `sourceName` varchar(255) DEFAULT NULL,
  `lineNumber` int DEFAULT NULL,
  PRIMARY KEY (`lineId`),
  KEY `line_proj_fr` (`projectId`),
  KEY `line_build_fr` (`buildId`),
  CONSTRAINT `line_build_fr` FOREIGN KEY (`buildId`) REFERENCES `build` (`buildId`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `line_proj_fr` FOREIGN KEY (`projectId`) REFERENCES `project` (`projectId`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=162226 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Table structure for project
-- ----------------------------
DROP TABLE IF EXISTS `project`;
CREATE TABLE `project` (
  `projectName` varchar(255) DEFAULT NULL,
  `projectId` int NOT NULL AUTO_INCREMENT,
  `projectLink` text,
  PRIMARY KEY (`projectId`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Table structure for testcase
-- ----------------------------
DROP TABLE IF EXISTS `testcase`;
CREATE TABLE `testcase` (
  `testcaseId` int NOT NULL AUTO_INCREMENT,
  `projectId` int DEFAULT NULL,
  `buildId` int DEFAULT NULL,
  `sourceName` varchar(255) DEFAULT NULL,
  `signature` varchar(255) DEFAULT NULL,
  `passed` int DEFAULT NULL,
  PRIMARY KEY (`testcaseId`),
  KEY `test_proj_fr` (`projectId`),
  KEY `test_build_fr` (`buildId`),
  CONSTRAINT `test_build_fr` FOREIGN KEY (`buildId`) REFERENCES `build` (`buildId`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `test_proj_fr` FOREIGN KEY (`projectId`) REFERENCES `project` (`projectId`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=20466 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

SET FOREIGN_KEY_CHECKS = 1;
