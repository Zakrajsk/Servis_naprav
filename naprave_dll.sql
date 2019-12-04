--
-- File generated with SQLiteStudio v3.2.1 on Wed Dec 4 16:19:17 2019
--
-- Text encoding used: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: Dobavitelj
DROP TABLE IF EXISTS Dobavitelj;
CREATE TABLE Dobavitelj (
    Id INTEGER PRIMARY KEY UNIQUE NOT NULL,
     Naziv TEXT NOT NULL UNIQUE, Telefon TEXT,
      Email TEXT);

-- Table: Lokacija
DROP TABLE IF EXISTS Lokacija;
CREATE TABLE Lokacija (
    Oznaka TEXT PRIMARY KEY UNIQUE NOT NULL);

-- Table: Nahajanje
DROP TABLE IF EXISTS Nahajanje;
CREATE TABLE Nahajanje (
    Od DATE NOT NULL,
    Do DATE,
    Inventarna_naprave NUMERIC REFERENCES Naprava (Inventarna) NOT NULL,
    Oznaka_lokacije TEXT REFERENCES Lokacija (Oznaka) NOT NULL);

-- Table: Naprava
DROP TABLE IF EXISTS Naprava;
CREATE TABLE Naprava (
    Inventarna NUMERIC PRIMARY KEY UNIQUE NOT NULL,
    Naziv TEXT NOT NULL,
    Tip TEXT NOT NULL,
    Stroskovno_mesto TEXT,
    Datum_garancije DATE,
    RLP INTEGER CHECK (RLP IN (12, 18, 24)),
    Serijska_st. TEXT NOT NULL UNIQUE);

-- Table: Popravilo
DROP TABLE IF EXISTS Popravilo;
CREATE TABLE Popravilo (
    St_narocila INTEGER PRIMARY KEY UNIQUE NOT NULL,
    Tip TEXT NOT NULL CHECK (tip IN ('RLP', 'Popravilo', 'Popravilo in RLP')),
    Inventarna_naprave NUMERIC REFERENCES Naprava (Inventarna) NOT NULL,
    Id_stopnje INTEGER REFERENCES Stopnja (Id) NOT NULL,
    Id_servisa INTEGER REFERENCES Servis (Id) NOT NULL);

-- Table: Servis
DROP TABLE IF EXISTS Servis;
CREATE TABLE Servis (
    d INTEGER PRIMARY KEY UNIQUE NOT NULL,
    Naziv TEXT UNIQUE, Telefon TEXT,
    Email TEXT);

-- Table: Skrbnik
DROP TABLE IF EXISTS Skrbnik;
CREATE TABLE Skrbnik (
    Id INTEGER PRIMARY KEY UNIQUE NOT NULL,
    Ime TEXT NOT NULL,
    Naziv TEXT,
    Email TEXT UNIQUE,
    Telefon TEXT UNIQUE);

-- Table: Skrbnistvo
DROP TABLE IF EXISTS Skrbnistvo;
CREATE TABLE Skrbnistvo (
    Od DATE NOT NULL,
    Do DATE,
    Id_skrbnika INTEGER REFERENCES Skrbnik (Id) NOT NULL,
    Inventarna_naprave NUMERIC REFERENCES Naprava (Inventarna) NOT NULL UNIQUE);

-- Table: Stopnja
DROP TABLE IF EXISTS Stopnja;
CREATE TABLE Stopnja (
    Id INTEGER PRIMARY KEY UNIQUE NOT NULL,
    Opis TEXT UNIQUE NOT NULL);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
