-- phpMyAdmin SQL Dump
-- version 4.7.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Aug 03, 2018 at 06:05 PM
-- Server version: 10.1.24-MariaDB
-- PHP Version: 7.1.6

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `ors`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`id`, `username`, `password`) VALUES
(1, 'admin', 'pupsjadmin123');

-- --------------------------------------------------------

--
-- Table structure for table `alembic_version`
--

CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `alembic_version`
--

INSERT INTO `alembic_version` (`version_num`) VALUES
('aaf74cfe333c');

-- --------------------------------------------------------

--
-- Table structure for table `equipment`
--

CREATE TABLE `equipment` (
  `id` int(11) NOT NULL,
  `equipmentPropertyNumber` varchar(50) NOT NULL,
  `equipmentName` varchar(50) NOT NULL,
  `quantity` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `equipment`
--

INSERT INTO `equipment` (`id`, `equipmentPropertyNumber`, `equipmentName`, `quantity`) VALUES
(7, 'PUP-ICTE-17-002', 'UNIC Projector', 1),
(8, 'PUP-LAB-0001', 'Laboratory Equipments', 1),
(9, 'PUP-ICTE-17-003', 'Television', 1);

-- --------------------------------------------------------

--
-- Table structure for table `facility`
--

CREATE TABLE `facility` (
  `id` int(11) NOT NULL,
  `facilityPropertyNumber` varchar(50) NOT NULL,
  `facilityName` varchar(50) NOT NULL,
  `availability` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `facility`
--

INSERT INTO `facility` (`id`, `facilityPropertyNumber`, `facilityName`, `availability`) VALUES
(1, 'PUP-FAC-0001', 'AVR-1', 'Yes'),
(2, 'PUP-FAC-0002', 'AVR-2', 'Yes'),
(3, 'PUP-FAC-0003', 'Gymnasium', 'Yes'),
(4, 'PUP-FAC-0004', 'COMPLAB-1', 'Yes'),
(5, 'PUP-FAC-0005', 'COMPLAB-2', 'Yes'),
(6, 'PUP-FAC-0006', 'COMPLAB-3', 'Yes'),
(7, 'PUP-FAC-0007', 'Lobby', 'Yes'),
(10, 'PUP-FAC-0008', 'Science Laboratory', 'Yes');

-- --------------------------------------------------------

--
-- Table structure for table `reservation`
--

CREATE TABLE `reservation` (
  `id` int(11) NOT NULL,
  `equipment_name` varchar(50) DEFAULT NULL,
  `facility_name` varchar(50) DEFAULT NULL,
  `studentNumber` varchar(15) NOT NULL,
  `purpose` varchar(100) NOT NULL,
  `dateFrom` date NOT NULL,
  `timeFrom` time NOT NULL,
  `timeTo` time NOT NULL,
  `reservation_date` datetime NOT NULL,
  `res_status` varchar(15) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `reservation`
--

INSERT INTO `reservation` (`id`, `equipment_name`, `facility_name`, `studentNumber`, `purpose`, `dateFrom`, `timeFrom`, `timeTo`, `reservation_date`, `res_status`) VALUES
(1, 'Laboratory Equipments', '--', '2014-00039-SJ-0', 'Academic', '2018-07-18', '15:00:00', '18:00:00', '2018-07-15 17:14:29', 'Done'),
(2, '--', 'AVR-1', '2014-00039-SJ-0', 'Academic', '2018-07-20', '14:00:00', '17:00:00', '2018-07-15 17:31:12', 'Done'),
(3, 'Projector', NULL, '2014-00001-SJ-0', 'Academic', '2018-07-14', '10:00:00', '15:00:00', '2018-07-13 00:00:00', 'Done'),
(4, 'Projector', NULL, '2014-00001-SJ-0', 'Academic', '2018-07-14', '10:00:00', '15:00:00', '2018-07-13 00:00:00', 'Done'),
(5, 'UNIC Projector', '--', '2014-00039-SJ-0', 'Academic', '2018-07-23', '14:00:00', '17:00:00', '2018-07-19 13:06:38', 'Done'),
(6, 'UNIC Projector', '--', '2014-00001-SJ-0', 'Academic', '2018-07-25', '16:01:00', '19:00:00', '2018-07-20 12:42:11', 'Done'),
(7, 'UNIC Projector', '--', '2014-00039-SJ-0', 'Academic', '2018-08-02', '09:00:00', '13:00:00', '2018-07-30 08:45:18', 'Done'),
(8, 'UNIC Projector', '--', '2014-00039-SJ-0', 'Academic', '2018-08-03', '13:00:00', '16:00:00', '2018-07-30 08:45:18', 'Active'),
(9, 'Projector', NULL, '2014-00001-SJ-0', 'Academic', '2018-07-30', '15:00:00', '18:00:00', '0000-00-00 00:00:00', ''),
(10, 'Laboratory Equipments', NULL, '2014-00039-SJ-0', 'Academic', '2018-07-30', '09:00:00', '12:00:00', '0000-00-00 00:00:00', ''),
(11, 'Laboratory Equipments', '--', '2014-00039-SJ-0', 'Academic', '2018-08-03', '15:00:00', '18:00:00', '2018-07-30 12:59:51', 'Active');

-- --------------------------------------------------------

--
-- Table structure for table `student`
--

CREATE TABLE `student` (
  `id` int(11) NOT NULL,
  `studentNumber` varchar(15) NOT NULL,
  `firstName` varchar(50) NOT NULL,
  `lastName` varchar(50) NOT NULL,
  `password` varchar(100) NOT NULL,
  `email` varchar(70) NOT NULL,
  `register_date` datetime NOT NULL,
  `courseAndSec` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `student`
--

INSERT INTO `student` (`id`, `studentNumber`, `firstName`, `lastName`, `password`, `email`, `register_date`, `courseAndSec`) VALUES
(2, '2014-00001-SJ-0', 'Jane', 'Doe', '$5$rounds=535000$Y/BZNprYFaHs/D6M$2vkFLrwJnx4Nf3TBjoOifPEFyTmg0vs6xIMz6xUZ9jC', 'jdoe@yahoo.com', '2018-07-01 14:01:37', 'BSIT 1-1'),
(3, '2014-00039-SJ-0', 'Carl Keneth', 'Baseleres', '$5$rounds=535000$.BRE3bTNPk4jGYO4$kQp7PQG2ezlGKeMIdZtsLfiNeDoRFIZfnpRlbw/FcP5', 'rapido97@yahoo.com', '2018-07-01 19:14:38', 'BSIT 4-1'),
(4, '2014-00021-SJ-0', 'Krista', 'Lazara', '$5$rounds=535000$.AHd0.3D8.obTOGU$yJn9zgnP1uHz/hSMAicQ.Ed6HykYkzJJHID6zpP6Oa5', 'kristalazara@yahoo.com', '2018-07-02 12:57:19', 'BSIT 4-1'),
(5, '2014-00002-SJ-0', 'Timothy', 'Villarez', '$5$rounds=535000$8ijFINs5/8uIfq/4$9OISno/tFUFo/CpwoT5QuovV1zomEubaLj/xBpQKtN4', 'timothy@gmail.com', '2018-07-02 14:00:51', 'BSIT 4-1'),
(6, '2014-00003-SJ-0', 'Jane', 'Doe', '$5$rounds=535000$NoYr6dza7dARqkkV$pfMQRM3/Xd9GeG3z.OgSQg4lJE7gCqb.HTgX1GzEUj9', 'jdoe@gmail.com', '2018-07-02 14:02:02', 'BSIT 1-1'),
(7, '2015-00165-SJ-0', 'Carl Angelo', 'Abucayan', '$5$rounds=535000$W4zCiiUWX/24fEry$mToksn1wrwTm2Olt1Quy1U3wXmWqo/fOqBCf6zb0S9C', 'ABUCAYAN@TEST.COM', '2018-07-23 19:08:00', 'BSIT 3-1');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `alembic_version`
--
ALTER TABLE `alembic_version`
  ADD PRIMARY KEY (`version_num`);

--
-- Indexes for table `equipment`
--
ALTER TABLE `equipment`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `equipmentPropertyNumber` (`equipmentPropertyNumber`);

--
-- Indexes for table `facility`
--
ALTER TABLE `facility`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `facilityPropertyNumber` (`facilityPropertyNumber`);

--
-- Indexes for table `reservation`
--
ALTER TABLE `reservation`
  ADD PRIMARY KEY (`id`),
  ADD KEY `studentNumber` (`studentNumber`);

--
-- Indexes for table `student`
--
ALTER TABLE `student`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `studentNumber` (`studentNumber`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admin`
--
ALTER TABLE `admin`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
--
-- AUTO_INCREMENT for table `equipment`
--
ALTER TABLE `equipment`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;
--
-- AUTO_INCREMENT for table `facility`
--
ALTER TABLE `facility`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;
--
-- AUTO_INCREMENT for table `reservation`
--
ALTER TABLE `reservation`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;
--
-- AUTO_INCREMENT for table `student`
--
ALTER TABLE `student`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;
--
-- Constraints for dumped tables
--

--
-- Constraints for table `reservation`
--
ALTER TABLE `reservation`
  ADD CONSTRAINT `reservation_ibfk_1` FOREIGN KEY (`studentNumber`) REFERENCES `student` (`studentNumber`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
