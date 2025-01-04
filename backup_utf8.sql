-- MySQL dump 10.13  Distrib 8.0.40, for Linux (x86_64)
--
-- Host: localhost    Database: yfinance_db
-- ------------------------------------------------------
-- Server version	8.0.40

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
-- Table structure for table `TickerData`
--

DROP TABLE IF EXISTS `TickerData`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `TickerData` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ticker` varchar(10) NOT NULL,
  `value` float DEFAULT NULL,
  `timestamp` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ticker` (`ticker`),
  CONSTRAINT `TickerData_ibfk_1` FOREIGN KEY (`ticker`) REFERENCES `Tickers` (`ticker`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `TickerData`
--

LOCK TABLES `TickerData` WRITE;
/*!40000 ALTER TABLE `TickerData` DISABLE KEYS */;
INSERT INTO `TickerData` VALUES (1,'GOOG',190.44,'2025-01-02 13:05:02'),(2,'GOOG',190.44,'2025-01-02 13:10:05');
/*!40000 ALTER TABLE `TickerData` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Tickers`
--

DROP TABLE IF EXISTS `Tickers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Tickers` (
  `ticker` varchar(10) NOT NULL,
  PRIMARY KEY (`ticker`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Tickers`
--

LOCK TABLES `Tickers` WRITE;
/*!40000 ALTER TABLE `Tickers` DISABLE KEYS */;
INSERT INTO `Tickers` VALUES ('GOOG');
/*!40000 ALTER TABLE `Tickers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `UserTickers`
--

DROP TABLE IF EXISTS `UserTickers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `UserTickers` (
  `user` varchar(255) NOT NULL,
  `ticker` varchar(10) NOT NULL,
  `max_value` float DEFAULT NULL,
  `min_value` float DEFAULT NULL,
  PRIMARY KEY (`user`,`ticker`),
  KEY `ticker` (`ticker`),
  CONSTRAINT `UserTickers_ibfk_1` FOREIGN KEY (`user`) REFERENCES `Users` (`email`) ON DELETE CASCADE,
  CONSTRAINT `UserTickers_ibfk_2` FOREIGN KEY (`ticker`) REFERENCES `Tickers` (`ticker`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `UserTickers`
--

LOCK TABLES `UserTickers` WRITE;
/*!40000 ALTER TABLE `UserTickers` DISABLE KEYS */;
INSERT INTO `UserTickers` VALUES ('masssifino@gmail.com','GOOG',170,0);
/*!40000 ALTER TABLE `UserTickers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Users`
--

DROP TABLE IF EXISTS `Users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Users` (
  `email` varchar(255) NOT NULL,
  `chat_id` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Users`
--

LOCK TABLES `Users` WRITE;
/*!40000 ALTER TABLE `Users` DISABLE KEYS */;
INSERT INTO `Users` VALUES ('masssifino@gmail.com',NULL);
/*!40000 ALTER TABLE `Users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-01-02 13:14:45
