/*
 Navicat MySQL Data Transfer

 Source Server         : php
 Source Server Type    : MySQL
 Source Server Version : 50553
 Source Host           : localhost:3306
 Source Schema         : test

 Target Server Type    : MySQL
 Target Server Version : 50553
 File Encoding         : 65001

 Date: 22/06/2024 22:39:04
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for keys
-- ----------------------------
DROP TABLE IF EXISTS `keys`;
CREATE TABLE `keys`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  `key` varchar(16) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `username`(`username`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 16 CHARACTER SET = latin1 COLLATE = latin1_swedish_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of keys
-- ----------------------------
INSERT INTO `keys` VALUES (11, 'admin', 'd45056f8c7f512a7');
INSERT INTO `keys` VALUES (13, 'lady_kill8', 'a5f68dd678f0da80');
INSERT INTO `keys` VALUES (14, 'lady_killer9', 'b2352c12756461d6');
INSERT INTO `keys` VALUES (15, 'lady_killer8', 'dcfd6dd02588392a');

-- ----------------------------
-- Table structure for nonces
-- ----------------------------
DROP TABLE IF EXISTS `nonces`;
CREATE TABLE `nonces`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nonce` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 13 CHARACTER SET = latin1 COLLATE = latin1_swedish_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of nonces
-- ----------------------------
INSERT INTO `nonces` VALUES (2, '23435', '2024-06-08 10:03:48');
INSERT INTO `nonces` VALUES (3, '1809270712', '2024-06-08 10:07:47');
INSERT INTO `nonces` VALUES (4, '2575201893', '2024-06-08 10:07:47');
INSERT INTO `nonces` VALUES (5, '2200641141', '2024-06-08 10:17:21');
INSERT INTO `nonces` VALUES (6, '2891884070', '2024-06-08 10:17:21');
INSERT INTO `nonces` VALUES (7, '1859223806', '2024-06-08 10:26:11');
INSERT INTO `nonces` VALUES (8, '1915055593', '2024-06-08 10:26:11');
INSERT INTO `nonces` VALUES (9, '198758498', '2024-06-08 10:28:20');
INSERT INTO `nonces` VALUES (10, '547369071', '2024-06-08 10:28:20');
INSERT INTO `nonces` VALUES (11, '3811672031', '2024-06-08 10:30:31');
INSERT INTO `nonces` VALUES (12, '3238707734', '2024-06-08 10:30:31');

-- ----------------------------
-- Table structure for passwords
-- ----------------------------
DROP TABLE IF EXISTS `passwords`;
CREATE TABLE `passwords`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  `password` varchar(16) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `username`(`username`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 12 CHARACTER SET = latin1 COLLATE = latin1_swedish_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of passwords
-- ----------------------------
INSERT INTO `passwords` VALUES (8, 'admin', 'admin');
INSERT INTO `passwords` VALUES (9, 'lady_killer9', 'osr86DV8');
INSERT INTO `passwords` VALUES (10, 'lady_kill8', 'h6Zt0ZIfhtjk');
INSERT INTO `passwords` VALUES (11, 'lady_kill11', 'XLkXm02N0KIOx3T9');

-- ----------------------------
-- Table structure for secrets
-- ----------------------------
DROP TABLE IF EXISTS `secrets`;
CREATE TABLE `secrets`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  `secret` varchar(32) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `username`(`username`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 14 CHARACTER SET = latin1 COLLATE = latin1_swedish_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of secrets
-- ----------------------------
INSERT INTO `secrets` VALUES (11, 'admin', 'admin');
INSERT INTO `secrets` VALUES (13, 'lady_kill10', 'a6ee9dbeb67bd06f70d8b6e32e7f5c22');

-- ----------------------------
-- Table structure for test
-- ----------------------------
DROP TABLE IF EXISTS `test`;
CREATE TABLE `test`  (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `pid` int(11) DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `pc` float(255, 0) DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 2 CHARACTER SET = latin1 COLLATE = latin1_swedish_ci ROW_FORMAT = Fixed;

-- ----------------------------
-- Records of test
-- ----------------------------
INSERT INTO `test` VALUES (1, 1, '0000-00-00 00:00:00', 0);

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `username` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `phone_number` varchar(11) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  PRIMARY KEY (`username`) USING BTREE
) ENGINE = MyISAM CHARACTER SET = latin1 COLLATE = latin1_swedish_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES ('admin', '2024-06-02 09:35:25', '13676859837');
INSERT INTO `users` VALUES ('lady_kill10', '2024-06-16 17:25:13', '13327789876');
INSERT INTO `users` VALUES ('lady_kill8', '2024-06-02 16:11:35', '13327789876');
INSERT INTO `users` VALUES ('lady_kill11', '2024-06-16 17:34:53', '13327789876');
INSERT INTO `users` VALUES ('lady_killer9', '2024-06-22 10:48:07', '13343554688');
INSERT INTO `users` VALUES ('lady_killer12', '2024-06-22 10:59:49', '13343554688');
INSERT INTO `users` VALUES ('l\' exp(710)', '2024-06-22 11:00:18', '13343554688');
INSERT INTO `users` VALUES ('l\' and exp(710)', '2024-06-22 11:00:30', '13343554688');
INSERT INTO `users` VALUES ('\' and exp(710)', '2024-06-22 11:00:56', '13343554688');
INSERT INTO `users` VALUES ('\' and exp(710)--', '2024-06-22 11:01:20', '13343554688');
INSERT INTO `users` VALUES ('\' and exp(~710)--', '2024-06-22 11:01:28', '13343554688');
INSERT INTO `users` VALUES ('lady_killer8', '2024-06-22 15:51:16', '13327789876');

SET FOREIGN_KEY_CHECKS = 1;
