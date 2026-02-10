#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

# This script creates additional sections for the comprehensive specification

sections = []

# Section 3: Workflows
section3 = """

---

## 3. WORKFLOWS DETALHADOS (PONTA A PONTA)

### 3.1 Workflow: Gestão de EPI (Ciclo Completo)

**Fluxo Principal:**

```
1. CADASTRO DE EPI
   ↓
2. ENTRADA EM ESTOQUE
   ↓
3. VINCULAÇÃO COM CA
   ↓
4. DEFINIÇÃO DE EPIs OBRIGATÓRIOS POR CARGO/RISCO
   ↓
5. ENTREGA AO COLABORADOR
   ├→ 5.1 Buscar colaborador (nome/CPF/QR Code)
   ├→ 5.2 Verificar EPIs obrigatórios para o cargo
   ├→ 5.3 Selecionar EPIs a entregar
   ├→ 5.4 Validar CA válido (BLOQUEIO se vencido)
   ├→ 5.5 Validar estoque disponível
   ├→ 5.6 Exibir termo de responsabilidade e orientações
   ├→ 5.7 Capturar assinatura eletrônica
   ├→ 5.8 Tirar foto (opcional mas recomendado)
   ├→ 5.9 Gerar Termo de Entrega (PDF)
   ├→ 5.10 Atualizar estoque (dar baixa)
   ├→ 5.11 Registrar entrega no histórico
   ├→ 5.12 Criar alerta de reposição (baseado em tempo de uso)
   └→ 5.13 Enviar e-mail com cópia do termo
   ↓
6. MONITORAMENTO DE VALIDADE
   ├→ Alerta 30 dias antes do vencimento (tempo de uso)
   ├→ Alerta 15 dias antes
   └→ Alerta vencido
   ↓
7. REPOSIÇÃO
   ├→ 7.1 Convocar colaborador para troca
   ├→ 7.2 Agendar entrega
   ├→ 7.3 Registrar devolução do EPI usado
   ├→ 7.4 Fotografar EPI devolvido (evidência desgaste)
   └→ 7.5 Nova entrega (voltar ao passo 5)
   ↓
8. AUDITORIA
   ├→ Consultar histórico completo
   ├→ Verificar assinaturas
   ├→ Exportar evidências
   └→ Relatório de conformidade
```

**Estados do EPI:**
- `Cadastrado`: EPI no catálogo, sem estoque
- `Em Estoque`: Disponível para entrega
- `Entregue`: Com colaborador, em uso
- `Vencido (CA)`: CA do fabricante venceu (bloqueado para entrega)
- `Vencido (Tempo de uso)`: Tempo de validade desde a entrega expirou
- `Devolvido`: Retornou ao estoque ou descartado
- `Descartado`: Fim de vida útil

**Exceções e Regras:**
- **EXC-01:** Se CA vencido → BLOQUEAR entrega + alerta vermelho + sugestão de comprar novo lote
- **EXC-02:** Se estoque zerado → alerta de ruptura + notificar almoxarife
- **EXC-03:** Se colaborador demitido → não permitir entrega
- **EXC-04:** Se colaborador já possui EPI válido do mesmo tipo → alertar (evitar duplicidade)
- **EXC-05:** Se falha na captura de assinatura → permitir retry ou assinatura manual (upload de foto assinada)

**Campos Obrigatórios no Termo de Entrega:**
1. Razão social da empresa cliente
2. Nome completo do colaborador, CPF, cargo, setor
3. Data e hora da entrega
4. Lista de EPIs entregues (tipo, CA, quantidade, validade)
5. Orientações de uso e conservação (padrão NR-06)
6. Declaração de recebimento e ciência
7. Assinatura eletrônica (com IP, timestamp, dispositivo)
8. Nome do técnico que entregou
9. QR Code para validação do termo

---

### 3.2 Workflow: Cautela de Equipamentos (Check-out / Check-in)

**Fluxo Principal:**

```
1. CADASTRO DE EQUIPAMENTO
   ├→ Tipo, patrimônio, série, fabricante
   ├→ Gerar QR Code
   ├→ Data próxima calibração
   └→ Status inicial: Disponível
   ↓
2. CHECK-OUT (EMPRÉSTIMO)
   ├→ 2.1 Escanear QR Code do equipamento (ou buscar por nome/patrimônio)
   ├→ 2.2 Verificar status = Disponível? (Se não, BLOQUEAR)
   ├→ 2.3 Verificar calibração válida? (Se não, BLOQUEAR + sugestão de calibrar)
   ├→ 2.4 Escanear QR Code do colaborador (ou buscar)
   ├→ 2.5 Informar data/hora prevista de devolução
   ├→ 2.6 Informar finalidade (ex: medição de ruído, inspeção, etc.)
   ├→ 2.7 Fotografar equipamento (estado atual)
   ├→ 2.8 Exibir Termo de Responsabilidade
   ├→ 2.9 Capturar assinatura eletrônica do colaborador
   ├→ 2.10 Gerar Termo de Empréstimo (PDF)
   ├→ 2.11 Atualizar status equipamento = Emprestado
   ├→ 2.12 Atualizar localização = "Com [Nome Colaborador]"
   ├→ 2.13 Criar alerta para data prevista de devolução
   └→ 2.14 Enviar e-mail ao colaborador com termo
   ↓
3. MONITORAMENTO DE DEVOLUÇÃO
   ├→ 1 dia antes da data prevista: lembrete
   ├→ Data prevista: alerta amarelo
   ├→ 1 dia após: alerta laranja + notificar gestor
   └→ 3 dias após: alerta vermelho + penalidade (se aplicável)
   ↓
4. CHECK-IN (DEVOLUÇÃO)
   ├→ 4.1 Escanear QR Code do equipamento
   ├→ 4.2 Conferir estado físico
   ├→ 4.3 Equipamento OK?
   │   ├→ SIM:
   │   │   ├→ Fotografar equipamento devolvido
   │   │   ├→ Capturar assinatura colaborador (confirmação devolução)
   │   │   ├→ Capturar assinatura técnico (confirmação recebimento)
   │   │   ├→ Atualizar status = Disponível
   │   │   ├→ Atualizar localização = Almoxarifado
   │   │   └→ Calcular tempo de uso
   │   └→ NÃO (AVARIA):
   │       ├→ Registrar ocorrência de avaria
   │       ├→ Descrever problema
   │       ├→ Fotografar dano
   │       ├→ Avaliar gravidade (leve, média, grave)
   │       ├→ Atualizar status = Em Manutenção
   │       ├→ Notificar gestor
   │       └→ Decidir: reparar, descartar, cobrar
   ↓
5. CALIBRAÇÃO (Quando Necessário)
   ├→ 5.1 Alerta 30 dias antes do vencimento
   ├→ 5.2 Agendar calibração com fornecedor
   ├→ 5.3 Atualizar status = Em Calibração
   ├→ 5.4 Registrar envio (data, fornecedor)
   ├→ 5.5 Aguardar retorno
   ├→ 5.6 Receber equipamento + certificado de calibração
   ├→ 5.7 Anexar certificado (PDF)
   ├→ 5.8 Atualizar data próxima calibração
   └→ 5.9 Atualizar status = Disponível
```

**Estados do Equipamento:**
- `Disponível`: Pronto para empréstimo
- `Emprestado`: Com colaborador
- `Em Manutenção`: Aguardando reparo
- `Em Calibração`: Enviado para calibração
- `Calibração Vencida`: Não pode ser emprestado
- `Descartado`: Fim de vida útil

**Regras de Bloqueio:**
- **BLQ-01:** Calibração vencida → bloquear empréstimo (criticidade alta)
- **BLQ-02:** Equipamento já emprestado → bloquear novo empréstimo
- **BLQ-03:** Avaria grave → bloquear até reparo
- **BLQ-04:** Equipamento perdido → bloquear + investigar

---

### 3.3 Workflow: ASO e Exames Ocupacionais

**Fluxo Principal:**

```
1. CONFIGURAÇÃO INICIAL (Por Cliente/Cargo)
   ├→ Definir matriz de exames por cargo/risco
   ├→ Periodicidade: admissional, periódico (6m, 1a, 2a), mudança função, demissional
   └→ Vincular com PGR/PCMSO
   ↓
2. GATILHOS DE CONVOCAÇÃO AUTOMÁTICA
   ├→ ADMISSIONAL:
   │   └→ Ao cadastrar novo colaborador → convocar imediatamente
   ├→ PERIÓDICO:
   │   └→ 30 dias antes do vencimento do ASO → convocar automaticamente
   ├→ MUDANÇA DE FUNÇÃO/RISCO:
   │   └→ Ao alterar cargo/setor com mudança de GHE → convocar
   └→ DEMISSIONAL:
       └→ Ao registrar demissão → convocar (se > 180 dias desde último exame)
   ↓
3. CONVOCAÇÃO
   ├→ 3.1 Sistema gera lista de convocados (automático via cron diário)
   ├→ 3.2 Notificar RH do cliente (e-mail com lista)
   ├→ 3.3 Notificar colaborador (e-mail/WhatsApp)
   ├→ 3.4 Status: Convocado
   └→ 3.5 Prazo para agendamento: 15 dias
   ↓
4. AGENDAMENTO
   ├→ 4.1 RH ou Técnico SST acessa agenda de clínicas
   ├→ 4.2 Seleciona colaborador convocado
   ├→ 4.3 Escolhe clínica, médico, data e horário
   ├→ 4.4 Confirma agendamento
   ├→ 4.5 Sistema envia confirmação ao colaborador (e-mail/WhatsApp)
   ├→ 4.6 Lembrete automático:
   │   ├→ 3 dias antes
   │   └→ 1 dia antes
   └→ 4.7 Status: Agendado
   ↓
5. REALIZAÇÃO DO EXAME
   ├→ 5.1 Colaborador comparece à clínica
   ├→ 5.2 Médico acessa sistema (prontuário do colaborador)
   ├→ 5.3 Visualiza histórico de exames, riscos, PGR
   ├→ 5.4 Realiza exame clínico
   ├→ 5.5 Solicita exames complementares (se necessário)
   ├→ 5.6 Registra resultados
   ├→ 5.7 Anexa laudos (PDF)
   ├→ 5.8 Avalia aptidão: Apto / Inapto / Apto com Restrições
   ├→ 5.9 Emite ASO
   ├→ 5.10 Captura assinatura eletrônica do médico (CRM obrigatório)
   ├→ 5.11 Gera PDF do ASO (assinado)
   ├→ 5.12 Status: Realizado
   └→ 5.13 Envia cópia ao colaborador e RH (e-mail automático)
   ↓
6. REGISTRO NO PRONTUÁRIO
   ├→ Salvar ASO no prontuário do colaborador
   ├→ Salvar laudos de exames complementares
   ├→ Atualizar data próximo exame (baseado em periodicidade)
   └→ Criar alerta para próximo vencimento
   ↓
7. INTEGRAÇÃO COM ESOCIAL (Opcional - Fase 3)
   ├→ Gerar evento S-2220 (Monitoramento de Saúde)
   ├→ Validar dados
   ├→ Enviar ao eSocial
   └→ Armazenar protocolo de retorno
   ↓
8. CONTROLE DE VENCIMENTO
   ├→ Motor de alertas monitora vencimentos diariamente
   ├→ 30 dias antes: alerta amarelo + e-mail RH
   ├→ 15 dias antes: alerta laranja + escalar para gestor
   ├→ Vencido: alerta vermelho + dashboard crítico
   └→ Convocar novamente (volta ao passo 2)
```

**Resultados Possíveis:**
- **Apto:** Colaborador pode trabalhar normalmente
- **Inapto:** Colaborador não pode exercer a função (afastamento ou realocação)
- **Apto com Restrições:** Colaborador pode trabalhar com limitações (ex: não levantar peso, não trabalhar em altura)

**Exceções:**
- **EXC-10:** Colaborador faltou → remarcar + notificar RH
- **EXC-11:** Inapto ou Apto com Restrições → notificar RH imediatamente + aguardar decisão (afastar, realocar)
- **EXC-12:** Exame complementar com alteração → médico orienta (reavaliar, encaminhar especialista)

---

### 3.4 Workflow: Gestão de Riscos (PGR)

**Fluxo Principal:**

```
1. LEVANTAMENTO PRELIMINAR
   ├→ Visita técnica ao cliente
   ├→ Mapeamento de processos
   ├→ Identificação de ambientes/setores
   └→ Cadastro de GHEs (Grupos Homogêneos de Exposição)
   ↓
2. IDENTIFICAÇÃO DE PERIGOS
   ├→ Para cada GHE/setor:
   │   ├→ Listar atividades
   │   ├→ Identificar perigos (físicos, químicos, biológicos, ergonômicos, acidentes)
   │   ├→ Registrar no inventário de riscos
   │   └→ Anexar fotos, documentos
   ↓
3. AVALIAÇÃO DE RISCOS
   ├→ Para cada risco identificado:
   │   ├→ Avaliar Severidade (1-5: desprezível a catastrófico)
   │   ├→ Avaliar Probabilidade (1-5: raro a quase certo)
   │   ├→ Calcular Nível de Risco (Severidade x Probabilidade)
   │   ├→ Classificar: Baixo, Médio, Alto, Crítico
   │   └→ Priorizar ações
   ↓
4. AVALIAÇÕES QUANTITATIVAS (Quando Aplicável)
   ├→ Ruído: Dosimetria (dB, dose, tempo de exposição)
   ├→ Calor: IBUTG
   ├→ Agentes químicos: ppm, mg/m³
   ├→ Iluminância: lux
   ├→ Vibração: m/s²
   ├→ Anexar laudos e certificados de calibração de equipamentos
   ↓
5. DEFINIÇÃO DE MEDIDAS DE CONTROLE
   ├→ Hierarquia de controle:
   │   ├→ 1. Eliminação do risco
   │   ├→ 2. EPC (Equipamento de Proteção Coletiva)
   │   ├→ 3. Medidas administrativas (procedimentos, treinamento)
   │   ├→ 4. EPI (última opção)
   ├→ Para cada risco:
   │   ├→ Definir medidas existentes
   │   ├→ Avaliar eficácia
   │   ├→ Propor melhorias
   │   └→ Vincular EPIs obrigatórios
   ↓
6. PLANO DE AÇÃO
   ├→ Para riscos Altos/Críticos:
   │   ├→ Criar ação corretiva
   │   ├→ Responsável, prazo, custo estimado
   │   ├→ Status: pendente, em andamento, concluída
   │   └→ Anexar evidências de conclusão
   ↓
7. ELABORAÇÃO DO DOCUMENTO PGR
   ├→ Gerar PDF com:
   │   ├→ Dados da empresa
   │   ├→ Inventário de riscos completo
   │   ├→ Avaliações quantitativas
   │   ├→ Medidas de controle
   │   ├→ Plano de ação
   │   ├→ Cronograma
   │   └→ Assinatura do técnico/engenheiro
   ├→ Versionamento (ex: PGR 2026 v1.0)
   └→ Armazenar no repositório de documentos
   ↓
8. APROVAÇÃO E ASSINATURA
   ├→ Enviar para assinatura:
   │   ├→ Técnico/Engenheiro de Segurança
   │   ├→ Médico Coordenador do PCMSO
   │   └→ Representante da empresa cliente (RH/Diretor)
   ├→ Assinatura eletrônica com trilha
   └→ Publicar versão final
   ↓
9. REVISÃO ANUAL OU POR EVENTO
   ├→ Gatilhos de revisão:
   │   ├→ Anual (obrigatório)
   │   ├→ Acidente grave
   │   ├→ Introdução de novo processo/equipamento
   │   ├→ Alteração de layout
   │   └→ Mudança de legislação
   ├→ Criar nova versão (ex: PGR 2027 v1.0 ou PGR 2026 v2.0)
   └→ Repetir fluxo a partir do passo 2
```

**Níveis de Risco (Matriz 5x5):**

| Probabilidade \ Severidade | 1-Desprezível | 2-Menor | 3-Moderado | 4-Maior | 5-Catastrófico |
|----------------------------|---------------|---------|------------|---------|----------------|
| 5-Quase Certo              | 5-Médio       | 10-Alto | 15-Alto    | 20-Crítico | 25-Crítico  |
| 4-Provável                 | 4-Baixo       | 8-Médio | 12-Alto    | 16-Alto | 20-Crítico  |
| 3-Possível                 | 3-Baixo       | 6-Médio | 9-Médio    | 12-Alto | 15-Alto     |
| 2-Improvável               | 2-Baixo       | 4-Baixo | 6-Médio    | 8-Médio | 10-Alto     |
| 1-Raro                     | 1-Baixo       | 2-Baixo | 3-Baixo    | 4-Baixo | 5-Médio     |

---

### 3.5 Workflow: eSocial SST (Geração e Envio de Eventos)

**Fluxo Principal:**

```
1. MAPEAMENTO INICIAL (Configuração - Uma Vez)
   ├→ Configurar credenciais eSocial (certificado digital A1/A3)
   ├→ Mapear campos do sistema → campos eSocial
   ├→ Configurar tabelas do eSocial (países, CBO, agentes nocivos, etc.)
   └→ Testar conexão com ambiente de produção restrita (opcional)
   ↓
2. GERAÇÃO DE EVENTOS (Automática ou Manual)
   ├→ 2.1 S-2210 (CAT):
   │   ├→ Gatilho: Registro de CAT no módulo M06
   │   ├→ Prazo: até 1 dia útil
   │   ├→ Dados: tipo acidente, data/hora, local, parte corpo, agente causador, testemunhas
   │
   ├→ 2.2 S-2220 (ASO - Monitoramento de Saúde):
   │   ├→ Gatilho: Emissão de ASO no módulo M05
   │   ├→ Prazo: até dia seguinte à realização do exame
   │   ├→ Dados: tipo exame, resultado (apto/inapto), exames complementares, médico CRM
   │
   └→ 2.3 S-2240 (Condições Ambientais - Agentes Nocivos):
       ├→ Gatilho: Admissão ou mudança de função/risco
       ├→ Prazo: conforme admissão ou mudança
       ├→ Dados: agentes nocivos, EPC, EPI (CA), intensidade/concentração, aposentadoria especial
   ↓
3. VALIDAÇÃO PRÉVIA
   ├→ Validar esquema XSD do eSocial
   ├→ Validar regras de negócio:
   │   ├→ CPF/CNPJ válidos?
   │   ├→ Datas consistentes?
   │   ├→ Valores dentro das tabelas eSocial?
   │   ├→ Campos obrigatórios preenchidos?
   │   └→ Relacionamentos corretos (ex: S-2240 exige S-2200 anterior)
   ├→ Gerar relatório de validação
   ├→ Se erro crítico → BLOQUEAR envio + notificar usuário
   └→ Se OK → prosseguir
   ↓
4. FILA DE ENVIO
   ├→ Adicionar evento na fila
   ├→ Priorizar: CAT = prioridade máxima, demais conforme prazo
   ├→ Status: Pendente
   └→ Processar fila (cron a cada hora ou botão manual)
   ↓
5. ENVIO AO ESOCIAL
   ├→ Montar XML conforme leiaute eSocial
   ├→ Assinar XML com certificado digital
   ├→ Enviar via WebService eSocial
   ├→ Status: Enviando
   ├→ Aguardar resposta (timeout 30s)
   ↓
6. PROCESSAMENTO DE RETORNO
   ├→ Retorno com Sucesso:
   │   ├→ Capturar protocolo de recebimento
   │   ├→ Armazenar número do recibo
   │   ├→ Status: Enviado com Sucesso
   │   ├→ Vincular protocolo ao evento
   │   └→ Notificar usuário (opcional)
   │
   └→ Retorno com Erro:
       ├→ Capturar código e descrição do erro
       ├→ Classificar erro:
       │   ├→ Crítico: dados incorretos, campos obrigatórios ausentes
       │   ├→ Atenção: avisos, inconsistências leves
       │   └→ Info: informações adicionais
       ├→ Status: Erro
       ├→ Sugerir correção (baseada em código de erro)
       ├→ Notificar usuário (e-mail + dashboard)
       └→ Permitir correção e reenvio
   ↓
7. CORREÇÃO E REENVIO (Se Necessário)
   ├→ Usuário acessa evento com erro
   ├→ Visualiza mensagem de erro detalhada
   ├→ Clica em "Corrigir"
   ├→ Sistema abre registro para edição
   ├→ Usuário corrige dados
   ├→ Salvar
   ├→ Revalidar
   ├→ Reenviar (volta ao passo 5)
   └→ Máximo de 3 tentativas automáticas (após, manual)
   ↓
8. MONITORAMENTO E RELATÓRIOS
   ├→ Dashboard eSocial:
   │   ├→ Total de eventos enviados (sucesso/erro)
   │   ├→ Pendentes de envio (com alerta se > 3 dias)
   │   ├→ Erros por tipo/código
   │   └→ Gráfico de evolução (eventos/mês)
   ├→ Relatório de Conformidade:
   │   ├→ % de eventos enviados no prazo
   │   ├→ Eventos com erro recorrente
   │   └→ Sugestões de melhoria
   └→ Exportação de lote (XML de todos os eventos)
```

**Tratamento de Erros Comuns:**

| Código Erro | Descrição | Ação Sugerida |
|-------------|-----------|---------------|
| REGRA_VALIDA_DT_ADMISSAO | Data de admissão inválida | Verificar data de admissão do colaborador no cadastro base |
| REGRA_VALIDA_CPF | CPF inválido | Corrigir CPF no cadastro do colaborador |
| REGRA_EXISTE_INFO_ANTERIOR | Falta evento anterior (ex: S-2200) | Enviar evento de admissão primeiro |
| REGRA_VALIDA_CODIGO_CBO | CBO inválido | Verificar tabela CBO e corrigir no cargo |
| REGRA_VALIDA_CA_EPI | CA do EPI inválido | Verificar CA no cadastro de EPI |

---

### 3.6 Workflow: Assinatura Eletrônica de Documentos

**Fluxo Principal:**

```
1. CRIAÇÃO DO DOCUMENTO
   ├→ Elaborar documento (PGR, PCMSO, termo, etc.)
   ├→ Salvar no repositório
   └→ Status: Rascunho
   ↓
2. SOLICITAR ASSINATURA
   ├→ Definir signatários:
   │   ├→ Nome, e-mail, perfil
   │   ├→ Ordem (sequencial ou paralelo)
   │   └→ Obrigatoriedade
   ├→ Enviar notificação aos signatários (e-mail + in-app)
   └→ Status: Aguardando Assinatura
   ↓
3. SIGNATÁRIO RECEBE NOTIFICAÇÃO
   ├→ E-mail: "Você tem um documento para assinar"
   ├→ Link para acessar sistema
   └→ Login obrigatório (autenticação)
   ↓
4. VISUALIZAÇÃO DO DOCUMENTO
   ├→ Signatário visualiza documento (PDF)
   ├→ Pode baixar para análise
   ├→ Lê termos de assinatura eletrônica
   └→ Decide: Assinar ou Rejeitar
   ↓
5. ASSINATURA
   ├→ Aceitar termos
   ├→ Opções:
   │   ├→ 5.1 Assinatura Simples (Canvas - desenho com mouse/touch)
   │   ├→ 5.2 Assinatura com Certificado Digital A1/A3 (futuro - V2)
   │   └→ 5.3 Assinatura com Biometria Facial (futuro - V3)
   ├→ Capturar dados:
   │   ├→ Timestamp preciso (millisegundos)
   │   ├→ IP do signatário
   │   ├→ User Agent (navegador, dispositivo)
   │   ├→ Geolocalização (se mobile e autorizado)
   │   ├→ Hash SHA-256 do documento assinado
   │   └→ Versão do documento
   ├→ Gerar certificado de assinatura
   ├→ Embed assinatura no PDF (visível)
   ├→ Armazenar evidências em tabela de auditoria (imutável)
   └→ Atualizar status da assinatura: Assinado
   ↓
6. PRÓXIMO SIGNATÁRIO (Se Sequencial)
   ├→ Notificar próximo signatário
   └→ Repetir passos 3-5
   ↓
7. FINALIZAÇÃO (Todas as Assinaturas Coletadas)
   ├→ Gerar documento final (PDF com todas as assinaturas embebidas)
   ├→ Gerar hash SHA-256 do documento final
   ├→ Gerar QR Code (para validação de autenticidade)
   ├→ Status: Assinado (Finalizado)
   ├→ Armazenar versão final no repositório
   ├→ Enviar cópia a todos os signatários (e-mail automático)
   └→ Documento fica imutável (não pode ser editado)
   ↓
8. VALIDAÇÃO EXTERNA (Por QR Code)
   ├→ Qualquer pessoa com documento PDF
   ├→ Escaneia QR Code no documento
   ├→ Sistema exibe:
   │   ├→ Título do documento
   │   ├→ Data de criação e finalização
   │   ├→ Lista de signatários (nome, data/hora assinatura)
   │   ├→ Hash do documento (verificação de integridade)
   │   └→ Status: Válido / Inválido
   └→ Se hash não bate → documento foi alterado após assinatura (ALERTA)
```

**Evidências Capturadas (Força Jurídica):**

Para cada assinatura, o sistema armazena:

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `documento_id` | ID do documento | 12345 |
| `signatario_id` | ID do usuário que assinou | user_789 |
| `signatario_nome` | Nome completo | Dr. Roberto Faria |
| `signatario_email` | E-mail | roberto.faria@clinica.com.br |
| `timestamp` | Data/hora precisa (UTC) | 2026-02-10T14:35:22.456Z |
| `ip_address` | IP de origem | 192.168.1.100 |
| `user_agent` | Navegador e dispositivo | Mozilla/5.0 (iPhone; iOS 15.0)... |
| `geolocalizacao` | Lat/Long (se disponível) | -23.550520, -46.633308 |
| `hash_documento` | SHA-256 do PDF no momento | a3f5d8e9b2c1... |
| `versao_documento` | Versão assinada | v1.0 |
| `tipo_assinatura` | Simples, Certificado, Biometria | simples |
| `assinatura_imagem` | Base64 da assinatura (se canvas) | data:image/png;base64,iVBOR... |
| `certificado_digital` | Dados do cert. (se aplicável) | null (V1), {...} (V2) |
| `status` | Status da assinatura | assinado |

**Validade Jurídica:**
- Conforme **MP 2.200-2/2001** (ICP-Brasil)
- Conforme **Lei 14.063/2020** (assinatura eletrônica simples, avançada e qualificada)
- Trilha de auditoria completa e imutável
- Hash garante integridade do documento
- Timestamp garante não-repúdio

---

"""

sections.append(section3)

# Write all sections to file
with open('ESPECIFICACAO_COMPLETA.md', 'a', encoding='utf-8') as f:
    for section in sections:
        f.write(section)

print(f"✓ Section 3 (Workflows) added successfully - {len(section3)} chars")

