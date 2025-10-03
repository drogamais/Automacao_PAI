CREATE TABLE `bronze_pai_performance` (
    `id_performance` INT(11) NOT NULL AUTO_INCREMENT,
    `loja_numero` INT(11) NOT NULL,
    `loja_nome` VARCHAR(255) NULL DEFAULT NULL,
    `data_ref` DATE NOT NULL,
    `indicador_nome` VARCHAR(255) NOT NULL,
    `unidade_medida` VARCHAR(50) NULL DEFAULT NULL,
    `metrica_geral` DECIMAL(22,4) NULL DEFAULT NULL,
    `metrica_media_loja_6m` DECIMAL(22,4) NULL DEFAULT NULL,
    `metrica_media_faixa_faturamento_6m` DECIMAL(22,4) NULL DEFAULT NULL,
    `metrica_media_febrafar_6m` DECIMAL(22,4) NULL DEFAULT NULL,
    PRIMARY KEY (`id_performance`) USING BTREE,
    UNIQUE INDEX `uk_loja_data_indicador` (`loja_numero`, `data_ref`, `indicador_nome`) USING BTREE
);