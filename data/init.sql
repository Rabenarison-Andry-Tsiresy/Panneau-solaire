use Energie-Solaire;

CREATE TABLE appareil (
    id_appareil INT PRIMARY KEY AUTO_INCREMENT,
    nom VARCHAR(255) NOT NULL,
    consommation FLOAT NOT NULL /* en watts */
);

CREATE TABLE appareil_usage (
    id_appareil_usage INT PRIMARY KEY AUTO_INCREMENT,
    id_appareil INT NOT NULL,
    heure_debut TIME NOT NULL,
    heure_fin TIME NOT NULL,
    FOREIGN KEY (id_appareil) REFERENCES appareil(id_appareil)
);
