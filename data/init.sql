DROP DATABASE EnergieSolaire;

GO

create DATABASE EnergieSolaire;

GO

use EnergieSolaire;

GO

-- Step 1: Create the parent table (if not already done)
CREATE TABLE appareil (
    id_appareil INT PRIMARY KEY IDENTITY(1,1),
    nom VARCHAR(255) NOT NULL,
    consommation FLOAT NOT NULL
);
GO

-- Step 2: Create the child table with foreign key
CREATE TABLE appareil_usage (
    id_appareil_usage INT PRIMARY KEY IDENTITY(1,1),
    id_appareil INT NOT NULL,
    heure_debut TIME NOT NULL,
    heure_fin TIME NOT NULL,
    FOREIGN KEY (id_appareil) REFERENCES appareil(id_appareil)
);
GO