-- phpMyAdmin SQL Dump
-- version 4.7.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 20, 2018 at 04:57 PM
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
-- Database: `capstone`
--

-- --------------------------------------------------------

--
-- Table structure for table `equipment`
--

CREATE TABLE `equipment` (
  `equipmentPropertyNumber` varchar(100) NOT NULL,
  `equipmentName` varchar(100) NOT NULL,
  `quantity` int(11) NOT NULL,
  `date_added` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `facility`
--

CREATE TABLE `facility` (
  `facilityPropertyNumber` varchar(100) NOT NULL,
  `facilityName` varchar(100) NOT NULL,
  `availability` varchar(50) NOT NULL,
  `date_added` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `facility`
--

INSERT INTO `facility` (`facilityPropertyNumber`, `facilityName`, `availability`, `date_added`) VALUES
('PUP-SJ-000234', 'Gymnasium', 'Yes', '2018-06-18 15:23:51');

-- --------------------------------------------------------

--
-- Table structure for table `student`
--

CREATE TABLE `student` (
  `studentNumber` varchar(15) NOT NULL,
  `firstName` text NOT NULL,
  `lastName` text NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(100) NOT NULL,
  `register_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `student`
--

INSERT INTO `student` (`studentNumber`, `firstName`, `lastName`, `email`, `password`, `register_date`) VALUES
('2014-00001-SJ-0', 'john', 'snow', 'jsnow@gmail.com', '$5$rounds=535000$Fvh27N/xXfqT11eI$58u7YOqpr62iji3vEKr.Xn7UxujWN8qR1kSGxkFK7e1', '2018-06-16 15:14:14'),
('2014-00002-SJ-0', 'jane', 'do', 'jdoe@yahoo.com', '$5$rounds=535000$0R/wg52ebNH9gWb3$U2blddcC/DwvgKxhxIkuV81jMCAt4.3Bj6n9D7hYJO3', '2018-06-16 16:27:10'),
('2014-00003-SJ-0', 'Sansa', 'Stark', 'sstark@gmail.com', '$5$rounds=535000$YLDG8U2u0Jl1WjV2$l0c1u30wvlJN1LOBmixbuGDDxGJA3bJSSpJcsUT1QND', '2018-06-16 16:35:57'),
('2014-00039-SJ-', 'sdaf', 'sdafsafsd', 'sdfsdfsdfs', '$5$rounds=535000$TV9ZMMDWtb5e6usw$hI8BJYHri/LjEuxmRsK8mg5GqJOpck1SVxV6f568hb4', '2018-06-15 03:41:18'),
('2014-00039-SJ-0', 'Carl Keneth', 'Baseleres', 'baseleres.ck@gmail.com', '$5$rounds=535000$jESS1pND5.RuxAUY$z7..XwHBwWJuTLB1wWUa3snfVUD6bT.CYh9mG8DDC08', '2018-06-15 03:14:50');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `equipment`
--
ALTER TABLE `equipment`
  ADD PRIMARY KEY (`equipmentPropertyNumber`);

--
-- Indexes for table `facility`
--
ALTER TABLE `facility`
  ADD PRIMARY KEY (`facilityPropertyNumber`);

--
-- Indexes for table `student`
--
ALTER TABLE `student`
  ADD PRIMARY KEY (`studentNumber`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
