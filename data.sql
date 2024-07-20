-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               10.4.32-MariaDB - mariadb.org binary distribution
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

-- Dumping data for table ag_data.jadwal: ~3 rows (approximately)
INSERT INTO `jadwal` (`id`, `tanggal`, `id_angkutan`, `id_rute`, `barang`, `jumlah_ton`) VALUES
	(4, '2024-07-23', 30, 1, 'sds', 0),
	(5, '2024-07-24', 30, 1, 'aceh', 0),
	(6, '2024-07-24', 30, 1, '', 0);

-- Dumping data for table ag_data.routes: ~2 rows (approximately)
INSERT INTO `routes` (`route_id`, `route_name`, `total_distance`, `created_at`) VALUES
	(1, 'Rute Distribusi Paket A', 0, '2024-07-08 18:47:35'),
	(2, 'Rute Pengangkutan Beras Senin', 0, '2024-07-08 23:59:18');

-- Dumping data for table ag_data.route_points: ~7 rows (approximately)
INSERT INTO `route_points` (`point_id`, `route_id`, `name`, `lat`, `lon`, `sequence`) VALUES
	(1, 1, 'Manggarai, Jalan Manggarai Utara I, RW 04, Manggarai, Tebet, South Jakarta, Special Region of Jakarta, Java, 12850, Indonesia', -6.21043, 106.85, 0),
	(2, 1, 'Bundaran HI, Jalan Mohammad Husni Thamrin, RW 05, Gondangdia, Menteng, Central Jakarta, Special Region of Jakarta, Java, 10350, Indonesia', -6.19186, 106.823, 1),
	(3, 1, 'Plaza Indonesia, Jalan Mohammad Husni Thamrin, RW 05, Gondangdia, Menteng, Central Jakarta, Special Region of Jakarta, Java, 10350, Indonesia', -6.19348, 106.823, 2),
	(4, 2, 'Banda Aceh, Aceh, Sumatra, Indonesia', 5.55285, 95.3193, 0),
	(5, 2, 'Lhokseumawe, Aceh, Sumatra, Indonesia', 5.17897, 97.1481, 1),
	(6, 2, 'Bireuen, Aceh, Sumatra, Indonesia', 5.08274, 96.5921, 2),
	(7, 2, 'Lhoksukon, Aceh Utara, Aceh, Sumatra, 24382, Indonesia', 5.02843, 97.3408, 3);

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
