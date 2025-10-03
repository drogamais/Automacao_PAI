CREATE TABLE `bronze_pai_financeiro` (
    `id_lancamento` INT(11) NOT NULL AUTO_INCREMENT,
    `loja_numero` INT(11) NOT NULL,
    `loja_nome` VARCHAR(255) NULL DEFAULT NULL COLLATE 'utf8mb4_uca1400_ai_ci',
    `data_ref` DATE NOT NULL,
    `indicador_nome` VARCHAR(255) NOT NULL COLLATE 'utf8mb4_uca1400_ai_ci',
    
    -- Colunas para o valor geral do mês
    `valor_geral` DECIMAL(18,2) NULL DEFAULT NULL,
    `percentual_geral` DECIMAL(10,4) NULL DEFAULT NULL,
    
    -- Colunas para a Média Loja Últimos 6 Meses
    `valor_media_loja_6m` DECIMAL(18,2) NULL DEFAULT NULL,
    `percentual_media_loja_6m` DECIMAL(10,4) NULL DEFAULT NULL,
    
    -- Colunas para a Média Faixa Faturamento Últimos 6 Meses
    `valor_media_faixa_faturamento_6m` DECIMAL(18,2) NULL DEFAULT NULL,
    `percentual_media_faixa_faturamento_6m` DECIMAL(10,4) NULL DEFAULT NULL,
    
    -- Colunas para a Média FEBRAFAR Últimos 6 Meses
    `valor_media_febrafar_6m` DECIMAL(18,2) NULL DEFAULT NULL,
    `percentual_media_febrafar_6m` DECIMAL(10,4) NULL DEFAULT NULL,
    
    PRIMARY KEY (`id_lancamento`) USING BTREE,
    UNIQUE INDEX `uk_loja_data_indicador` (`loja_numero`, `data_ref`, `indicador_nome`) USING BTREE
)
COLLATE='utf8mb4_uca1400_ai_ci'
ENGINE=InnoDB;