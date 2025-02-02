-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               8.0.30 - MySQL Community Server - GPL
-- Server OS:                    Win64
-- HeidiSQL Version:             12.6.0.6765
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

-- Dumping structure for table ag_data.jadwal
CREATE TABLE IF NOT EXISTS `jadwal` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tanggal` date NOT NULL,
  `id_angkutan` int NOT NULL,
  `id_rute` int NOT NULL,
  `barang` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `jumlah_ton` float DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table ag_data.jadwal: ~3 rows (approximately)
INSERT INTO `jadwal` (`id`, `tanggal`, `id_angkutan`, `id_rute`, `barang`, `jumlah_ton`) VALUES
	(4, '2024-07-23', 30, 1, 'sds', 0),
	(5, '2024-07-24', 30, 1, 'aceh', 0),
	(6, '2024-07-24', 30, 1, '', 0);

-- Dumping structure for table ag_data.routes
CREATE TABLE IF NOT EXISTS `routes` (
  `route_id` int NOT NULL AUTO_INCREMENT,
  `route_name` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `total_distance` float DEFAULT '0',
  `created_at` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`route_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table ag_data.routes: ~2 rows (approximately)
INSERT INTO `routes` (`route_id`, `route_name`, `total_distance`, `created_at`) VALUES
	(1, 'Rute Distribusi Paket A', 0, '2024-07-08 18:47:35'),
	(2, 'Rute Pengangkutan Beras Senin', 0, '2024-07-08 23:59:18'),
	(5, 'rute 22', 0, '2025-01-30 15:57:10');

-- Dumping structure for table ag_data.route_points
CREATE TABLE IF NOT EXISTS `route_points` (
  `point_id` int NOT NULL AUTO_INCREMENT,
  `route_id` int NOT NULL,
  `name` text COLLATE utf8mb4_general_ci NOT NULL,
  `lat` double NOT NULL,
  `lon` double NOT NULL,
  `sequence` int DEFAULT '0',
  `status` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`point_id`),
  KEY `route_id` (`route_id`),
  CONSTRAINT `route_points_ibfk_1` FOREIGN KEY (`route_id`) REFERENCES `routes` (`route_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table ag_data.route_points: ~7 rows (approximately)
INSERT INTO `route_points` (`point_id`, `route_id`, `name`, `lat`, `lon`, `sequence`, `status`) VALUES
	(1, 1, 'Manggarai, Jalan Manggarai Utara I, RW 04, Manggarai, Tebet, South Jakarta, Special Region of Jakarta, Java, 12850, Indonesia', -6.21043, 106.85, 0, 'Pengepul'),
	(2, 1, 'Bundaran HI, Jalan Mohammad Husni Thamrin, RW 05, Gondangdia, Menteng, Central Jakarta, Special Region of Jakarta, Java, 10350, Indonesia', -6.19186, 106.823, 1, 'Pengepul'),
	(3, 1, 'Plaza Indonesia, Jalan Mohammad Husni Thamrin, RW 05, Gondangdia, Menteng, Central Jakarta, Special Region of Jakarta, Java, 10350, Indonesia', -6.19348, 106.823, 2, 'Pabrik'),
	(4, 2, 'Banda Aceh, Aceh, Sumatra, Indonesia', 5.55285, 95.3193, 0, NULL),
	(5, 2, 'Lhokseumawe, Aceh, Sumatra, Indonesia', 5.17897, 97.1481, 1, NULL),
	(6, 2, 'Bireuen, Aceh, Sumatra, Indonesia', 5.08274, 96.5921, 2, NULL),
	(7, 2, 'Lhoksukon, Aceh Utara, Aceh, Sumatra, 24382, Indonesia', 5.02843, 97.3408, 3, NULL),
	(8, 5, 'Banda Aceh, Aceh, Sumatra, Indonesia', 5.5528455, 95.3192908, 0, 'Pengepul'),
	(9, 5, 'Langsa, Aceh, Sumatra, 24412, Indonesia', 4.4730892, 97.9681841, 1, 'Pengepul'),
	(10, 5, 'City of Medan, North Sumatra, Sumatra, Indonesia', 3.5896654, 98.6738261, 2, 'Pengepul');

-- Dumping structure for table ag_data.transport
CREATE TABLE IF NOT EXISTS `transport` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nama_kendaraan` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `plat_nomor` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `kondisi` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `nama_supir` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `nomor_telepon` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `status_keberangkatan` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table ag_data.transport: ~6 rows (approximately)
INSERT INTO `transport` (`id`, `nama_kendaraan`, `plat_nomor`, `kondisi`, `nama_supir`, `nomor_telepon`, `status_keberangkatan`) VALUES
	(30, 'Van B', 'B 5678 EF', 'Baik', 'Jane Doe', '081234567891', 'Istirahat'),
	(31, 'Motor C', 'B 9101 GH', 'Kurang Baik', 'Jim Beam', '081234567892', 'Tidak Masuk'),
	(32, 'Truck A', 'B 1234 CD', 'Baik', 'John Doe', '081234567890', 'Berangkat'),
	(33, 'Van B', 'B 5678 EF', 'Baik', 'Jane Doe', '081234567891', 'Istirahat'),
	(34, 'Okejlk', 'jlk', 'jlk', ';j', 'kjmlkj', 'klj'),
	(35, 'klk', 'jlk', 'j', 'lkj', 'lkj', 'lk');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
