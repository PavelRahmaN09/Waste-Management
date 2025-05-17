-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 17, 2025 at 06:23 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `waste_management`
--

-- --------------------------------------------------------

--
-- Table structure for table `garbage_collection`
--

CREATE TABLE `garbage_collection` (
  `id` int(11) NOT NULL,
  `center_id` int(11) DEFAULT NULL,
  `quantity` int(11) DEFAULT NULL,
  `total_amount` decimal(10,2) DEFAULT NULL,
  `date` date DEFAULT NULL,
  `garbage_pic` varchar(255) DEFAULT NULL,
  `picked_up_status` tinyint(1) DEFAULT NULL,
  `latitude` float DEFAULT NULL,
  `longitude` float DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `garbage_type_id` int(11) DEFAULT NULL,
  `sale_price` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `garbage_collection`
--

INSERT INTO `garbage_collection` (`id`, `center_id`, `quantity`, `total_amount`, `date`, `garbage_pic`, `picked_up_status`, `latitude`, `longitude`, `user_id`, `garbage_type_id`, `sale_price`) VALUES
(1, 5, 150, 3000.00, '2025-02-09', 'plastic.jpg', 1, 25.7475, 89.2548, NULL, 1, 5.5),
(2, 6, 80, 4000.00, '2025-03-09', 'aluminum.jpg', 1, 25.7475, 89.2548, 3, 3, 5.2),
(3, 7, 100, 3000.00, '2025-04-09', 'metal.png', 1, 25.7475, 89.2548, NULL, 2, 12.5),
(6, 5, 20, 1600.00, '2025-06-09', 'metal.png', 1, 25.7475, 89.2548, 3, 2, 12.5),
(7, 6, 60, 3000.00, '2025-07-09', 'organic.jpg', 0, 25.7475, 89.2548, NULL, 1, 5.5),
(8, 7, 55, 847.00, '2025-08-14', '8_arduino_uno.png', 1, 25.7475, 89.2548, 3, 5, 15.4),
(9, 8, 12, 184.80, '2025-09-11', '9_charging_module.png', 1, 25.7474, 89.2548, 3, 5, 15.4),
(11, NULL, 21, 42.00, '2025-03-22', 'rgb.png', 0, 25.7475, 89.2548, 3, 6, 2),
(12, NULL, 30, 234.00, '2025-03-23', 'default.jpg', 0, 25.7475, 89.2548, 3, 4, 7.8),
(16, NULL, 233, 1817.40, '2025-04-11', 'usb.png', 2, 25.7475, 89.2548, 3, 4, 7.8),
(17, NULL, 890, 11125.00, '2015-06-10', 'buzzer.png', 0, 25.7422, 89.2503, 3, 2, 12.5),
(18, NULL, 188, 526.40, '2025-04-16', 'default.jpg', 1, 25.7475, 89.2562, 3, 8, 2.8),
(19, 7, 95, 190.00, '2025-04-16', 'default.jpg', 1, 25.7474, 89.2548, 3, 6, 2);

-- --------------------------------------------------------

--
-- Table structure for table `garbage_types`
--

CREATE TABLE `garbage_types` (
  `id` int(11) NOT NULL,
  `garbage_type` varchar(255) NOT NULL,
  `sale_price` decimal(10,2) NOT NULL,
  `garbage_pic` varchar(255) DEFAULT 'default.png'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `garbage_types`
--

INSERT INTO `garbage_types` (`id`, `garbage_type`, `sale_price`, `garbage_pic`) VALUES
(1, 'Plastic', 5.50, 'plastic.png'),
(2, 'Metal', 12.50, 'metal.png'),
(3, 'Paper', 5.20, 'paper.png'),
(4, 'Glass', 7.80, 'default.jpg'),
(5, 'Electronics', 15.40, 'electrical.png'),
(6, 'Organic Waste', 2.00, 'organic.png'),
(8, 'Others', 2.80, 'others.jpg');

-- --------------------------------------------------------

--
-- Table structure for table `monthly_sales`
--

CREATE TABLE `monthly_sales` (
  `id` int(11) NOT NULL,
  `center_id` int(11) DEFAULT NULL,
  `garbage_type_id` int(11) DEFAULT NULL,
  `january` decimal(10,2) DEFAULT 0.00,
  `february` decimal(10,2) DEFAULT 0.00,
  `march` decimal(10,2) DEFAULT 0.00,
  `april` decimal(10,2) DEFAULT 0.00,
  `may` decimal(10,2) DEFAULT 0.00,
  `june` decimal(10,2) DEFAULT 0.00,
  `july` decimal(10,2) DEFAULT 0.00,
  `august` decimal(10,2) DEFAULT 0.00,
  `september` decimal(10,2) DEFAULT 0.00,
  `october` decimal(10,2) DEFAULT 0.00,
  `november` decimal(10,2) DEFAULT 0.00,
  `december` decimal(10,2) DEFAULT 0.00,
  `total_sales` decimal(10,2) DEFAULT 0.00,
  `yearly_sales` decimal(10,2) DEFAULT 0.00
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `monthly_sales`
--

INSERT INTO `monthly_sales` (`id`, `center_id`, `garbage_type_id`, `january`, `february`, `march`, `april`, `may`, `june`, `july`, `august`, `september`, `october`, `november`, `december`, `total_sales`, `yearly_sales`) VALUES
(4, 5, 1, 200.00, 150.00, 180.00, 220.00, 250.00, 300.00, 280.00, 260.00, 210.00, 230.00, 190.00, 270.00, 0.00, 0.00),
(5, 6, 2, 100.00, 90.00, 95.00, 105.00, 120.00, 140.00, 130.00, 110.00, 90.00, 85.00, 100.00, 127.00, 0.00, 0.00),
(6, 7, 3, 150.00, 160.00, 170.00, 180.00, 190.00, 200.00, 210.00, 220.00, 180.00, 175.00, 165.00, 210.00, 0.00, 0.00),
(9, 5, 6, 90.00, 100.00, 110.00, 120.00, 130.00, 140.00, 150.00, 160.00, 140.00, 135.00, 125.00, 137.00, 0.00, 0.00),
(10, 6, 7, 400.00, 420.00, 440.00, 460.00, 480.00, 500.00, 520.00, 540.00, 510.00, 490.00, 470.00, 574.00, 0.00, 0.00),
(11, 7, 8, 80.00, 85.00, 90.00, 95.00, 100.00, 110.00, 115.00, 120.00, 105.00, 100.00, 95.00, 109.00, 0.00, 0.00),
(12, 8, 9, 130.00, 140.00, 150.00, 160.00, 170.00, 180.00, 190.00, 200.00, 175.00, 165.00, 155.00, 187.00, 0.00, 0.00),
(18, 7, 8, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 847.00, 0.00, 0.00, 0.00, 0.00, 847.00, 2025.00),
(19, NULL, 8, 0.00, 0.00, 0.00, 526.40, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 526.40, 2025.00),
(21, 7, 6, 0.00, 0.00, 0.00, 190.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 190.00, 2025.00);

-- --------------------------------------------------------

--
-- Table structure for table `recycling_centers`
--

CREATE TABLE `recycling_centers` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `address` varchar(255) NOT NULL,
  `contact` varchar(20) NOT NULL,
  `email` varchar(255) NOT NULL,
  `total_income` double DEFAULT NULL,
  `latitude` float DEFAULT NULL,
  `longitude` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `recycling_centers`
--

INSERT INTO `recycling_centers` (`id`, `name`, `address`, `contact`, `email`, `total_income`, `latitude`, `longitude`) VALUES
(5, 'Zero Waste Solutions', '202 Zero Dr, Portland, OR', '321-654-9870', 'info@zerowaste.com', 250000, 18.1212, 35.8388),
(6, 'Recycle It Now', '303 Recycle Ave, Miami, fL', '567-890-1234', 'contact@recycleitnow.com', 120000, 0, 0),
(7, 'WasteNot Recycling', '404 Waste St, San Diego, CA', '876-543-2109', 'info@wastenotrecycling.com', 191037, 117.146, 32.8388),
(8, 'Sustainable Future Recycling', '505 Future Blvd, Boston, MA', '543-210-9876', 'contact@sustainablefuture.com', 220000, 15.1212, 31.8388),
(12, 'jankshop demo', 'Los Angeles ', '09675674', 'sam@gmail.com', 0, 25.7475, 89.2562);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `profile_pic` text DEFAULT NULL,
  `first_name` varchar(50) NOT NULL,
  `middle_name` varchar(50) DEFAULT NULL,
  `last_name` varchar(50) NOT NULL,
  `role` enum('admin','member') NOT NULL DEFAULT 'member',
  `gender` enum('male','female','other') NOT NULL,
  `birthday` date NOT NULL,
  `contact` varchar(20) NOT NULL,
  `email` varchar(100) NOT NULL,
  `address` text NOT NULL,
  `location` text NOT NULL,
  `longitude` float DEFAULT NULL,
  `latitude` float DEFAULT NULL,
  `username` varchar(50) NOT NULL,
  `password` text NOT NULL,
  `account_status` enum('active','inactive') NOT NULL DEFAULT 'active',
  `total_income` float DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `profile_pic`, `first_name`, `middle_name`, `last_name`, `role`, `gender`, `birthday`, `contact`, `email`, `address`, `location`, `longitude`, `latitude`, `username`, `password`, `account_status`, `total_income`, `created_at`) VALUES
(3, NULL, 'Leroy', 'Azalia Spence', 'Wolfe', 'member', 'male', '1970-01-06', 'In vero sint dolore', 'quzocu@mailinator.com', 'Et esse doloribus a', 'Unknown', 89.2562, 25.7475, 'member', 'scrypt:32768:8:1$RWFA1rQBdpnwSNMn$ee88b3eec36cab616653bf022b0b97f754902391da649923e76215b9cbb637675bc9d892c3087aae979abf1314939e01d15e0f3b64ce93e17fee6e3a8401deaf', 'inactive', 0, '2025-03-08 18:42:20'),
(4, NULL, 'Maia', 'Jameson Fox', 'Ellis', 'admin', 'male', '2002-01-02', 'Nostrum recusandae ', 'tarisy@mailinator.com', 'Nostrud velit in co', 'Unknown', 89.2562, 25.7475, 'admin', 'scrypt:32768:8:1$mzLm2ikL8P2oXjUv$9b7d6cc54ab68e451db7671c86ba7b6ea2671f6805e105300e35c858c9a9ce7e7b7b59614ba4130b97f5891a3469a6d3e141f32bcba314b86c77e0600dcc1f0d', 'active', 0, '2025-03-08 18:42:48');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `garbage_collection`
--
ALTER TABLE `garbage_collection`
  ADD PRIMARY KEY (`id`),
  ADD KEY `center_id` (`center_id`);

--
-- Indexes for table `garbage_types`
--
ALTER TABLE `garbage_types`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `monthly_sales`
--
ALTER TABLE `monthly_sales`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_monthly_sales` (`center_id`,`garbage_type_id`,`yearly_sales`),
  ADD KEY `garbage_type_id` (`garbage_type_id`);

--
-- Indexes for table `recycling_centers`
--
ALTER TABLE `recycling_centers`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `garbage_collection`
--
ALTER TABLE `garbage_collection`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- AUTO_INCREMENT for table `garbage_types`
--
ALTER TABLE `garbage_types`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `monthly_sales`
--
ALTER TABLE `monthly_sales`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=22;

--
-- AUTO_INCREMENT for table `recycling_centers`
--
ALTER TABLE `recycling_centers`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `garbage_collection`
--
ALTER TABLE `garbage_collection`
  ADD CONSTRAINT `garbage_collection_ibfk_1` FOREIGN KEY (`center_id`) REFERENCES `recycling_centers` (`id`);

--
-- Constraints for table `monthly_sales`
--
ALTER TABLE `monthly_sales`
  ADD CONSTRAINT `monthly_sales_ibfk_1` FOREIGN KEY (`center_id`) REFERENCES `recycling_centers` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
