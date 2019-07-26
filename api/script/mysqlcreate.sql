SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema gsenha
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `gsenha` ;

-- -----------------------------------------------------
-- Schema gsenha
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `gsenha` ;
USE `gsenha` ;

--
-- Table structure for table `Usuarios`
--

DROP TABLE IF EXISTS `Usuarios`;
CREATE TABLE `Usuarios` (
  `idUsuario` int(11) NOT NULL AUTO_INCREMENT,
  `NomeUsuario` varchar(45) NOT NULL,
  `Email` varchar(45) NOT NULL,
  `username` varchar(45) NOT NULL,
  `PublicKey` varchar(1500) NOT NULL,
  `token` varchar(65) NOT NULL DEFAULT '0',
  `hash` varchar(65) NOT NULL DEFAULT '0',
  PRIMARY KEY (`idUsuario`),
  UNIQUE KEY `username_UNIQUE` (`username`)
) ENGINE=InnoDB;

--
-- Table structure for table `Grupos`
--

DROP TABLE IF EXISTS `Grupos`;
CREATE TABLE `Grupos` (
  `idGrupo` int(11) NOT NULL AUTO_INCREMENT,
  `NomeGrupo` varchar(45) NOT NULL,
  PRIMARY KEY (`idGrupo`),
  UNIQUE KEY `NomeGrupo_UNIQUE` (`NomeGrupo`)
) ENGINE=InnoDB;

--
-- Table structure for table `Pastas`
--

DROP TABLE IF EXISTS `Pastas`;
CREATE TABLE `Pastas` (
  `idPasta` int(11) NOT NULL AUTO_INCREMENT,
  `lft` int(11) NOT NULL,
  `rgt` int(11) NOT NULL,
  `NomePasta` varchar(200) NOT NULL,
  `Usuarios_idUsuario` int(11) DEFAULT NULL,
  `Grupos_idGrupo` int(11) DEFAULT NULL,
  PRIMARY KEY (`idPasta`),
  UNIQUE KEY `NomePasta` (`NomePasta`),
  KEY `fk_Pastas_Usuarios1_idx` (`Usuarios_idUsuario`),
  KEY `fk_Pastas_Grupos1_idx` (`Grupos_idGrupo`),
  CONSTRAINT `fk_Pastas_Grupos1` FOREIGN KEY (`Grupos_idGrupo`) REFERENCES `Grupos` (`idGrupo`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_Pastas_Usuarios1` FOREIGN KEY (`Usuarios_idUsuario`) REFERENCES `Usuarios` (`idUsuario`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB;

--
-- Table structure for table `Passwords`
--

DROP TABLE IF EXISTS `Passwords`;
CREATE TABLE `Passwords` (
  `idPassword` int(11) NOT NULL AUTO_INCREMENT,
  `Usuario_idUsuario` int(11) NOT NULL,
  `Grupo_idGrupo` int(11) NOT NULL,
  `Pastas_idPastas` int(11) NOT NULL,
  `idCompartilhado` int(11) DEFAULT NULL,
  `senha` varchar(1000) NOT NULL,
  `url` varchar(1000) DEFAULT NULL,
  `login` varchar(1000) DEFAULT NULL,
  `descricao` varchar(1000) DEFAULT NULL,
  `nome` varchar(100) NOT NULL,
  PRIMARY KEY (`idPassword`),
  UNIQUE KEY `idPassword` (`idPassword`),
  UNIQUE KEY `nome_unico` (`nome`,`Usuario_idUsuario`,`Grupo_idGrupo`,`Pastas_idPastas`),
  KEY `fk_Password_Usuario_idx` (`Usuario_idUsuario`),
  KEY `fk_Password_Grupo1_idx` (`Grupo_idGrupo`),
  KEY `fk_Passwords_Pastas1_idx` (`Pastas_idPastas`),
  CONSTRAINT `fk_Passwords_Pastas1` FOREIGN KEY (`Pastas_idPastas`) REFERENCES `Pastas` (`idPasta`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_Password_Grupo1` FOREIGN KEY (`Grupo_idGrupo`) REFERENCES `Grupos` (`idGrupo`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_Password_Usuario` FOREIGN KEY (`Usuario_idUsuario`) REFERENCES `Usuarios` (`idUsuario`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB;

--
-- Table structure for table `Usuario_Grupo`
--

DROP TABLE IF EXISTS `Usuario_Grupo`;
CREATE TABLE `Usuario_Grupo` (
  `idUsuario_Grupo` int(11) NOT NULL AUTO_INCREMENT,
  `Usuarios_idUsuario` int(11) NOT NULL,
  `Grupos_idGrupo` int(11) NOT NULL,
  PRIMARY KEY (`idUsuario_Grupo`),
  KEY `fk_Usuario_Grupo_Usuarios1_idx` (`Usuarios_idUsuario`),
  KEY `fk_Usuario_Grupo_Grupos1_idx` (`Grupos_idGrupo`),
  CONSTRAINT `fk_Usuario_Grupo_Grupos1` FOREIGN KEY (`Grupos_idGrupo`) REFERENCES `Grupos` (`idGrupo`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_Usuario_Grupo_Usuarios1` FOREIGN KEY (`Usuarios_idUsuario`) REFERENCES `Usuarios` (`idUsuario`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB;


INSERT INTO `gsenha`.`Grupos` (`NomeGrupo`) VALUES ("Personal");

INSERT INTO `gsenha`.`Pastas`(`lft`,`rgt`,`NomePasta`,`Usuarios_idUsuario`,`Grupos_idGrupo`)
VALUES ("0","0","/",NULL,NULL);

LOCK TABLES `gsenha`.`Pastas` WRITE;
SELECT @myLeft:= lft FROM `gsenha`.`Pastas` WHERE NomePasta = "/";
UPDATE `gsenha`.`Pastas` SET rgt = (rgt + 2) WHERE rgt > @myLeft;
UPDATE `gsenha`.`Pastas` SET lft = (lft + 2) WHERE lft > @myLeft;
INSERT INTO `gsenha`.`Pastas` (`NomePasta`,`lft`,`rgt`,`Grupos_idGrupo`,`Usuarios_idUsuario`) VALUES ("/Personal",@myLeft +1,@myLeft +2,NULL,NULL);
UNLOCK TABLES;

LOCK TABLES `gsenha`.`Pastas` WRITE;
SELECT @myLeft:= lft FROM `gsenha`.`Pastas` WHERE NomePasta = "/";
UPDATE `gsenha`.`Pastas` SET rgt = (rgt + 2) WHERE rgt > @myLeft;
UPDATE `gsenha`.`Pastas` SET lft = (lft + 2) WHERE lft > @myLeft;
INSERT INTO `gsenha`.`Pastas` (`NomePasta`,`lft`,`rgt`,`Grupos_idGrupo`,`Usuarios_idUsuario`) VALUES ("/Shared",@myLeft +1,@myLeft +2,NULL,NULL);
UNLOCK TABLES;
