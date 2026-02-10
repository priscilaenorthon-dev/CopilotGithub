# ESPECIFICAÇÃO COMPLETA DO SISTEMA SST SAAS

**Sistema de Gestão de Segurança e Saúde do Trabalho**  
**Versão:** 1.0  
**Data:** Fevereiro 2026  
**Stack Técnico:** PHP + MySQL (XAMPP) com evolução para SaaS Cloud

---

## SUMÁRIO EXECUTIVO

Este documento apresenta a especificação completa de um sistema SaaS para Gestão de Segurança e Saúde do Trabalho (SST), desenvolvido para prestadores de serviços de SST que atendem múltiplas empresas clientes. O sistema foi projetado para funcionar inicialmente em ambiente XAMPP (PHP + MySQL) com arquitetura preparada para evolução futura para SaaS cloud-native.

**Principais características:**
- Multi-tenant com isolamento completo por cliente
- Conformidade com NR-06 (EPI), NR-07 (PCMSO) e eSocial SST
- Automação de alertas e workflows
- Assinatura eletrônica e trilha de auditoria completa
- Interface moderna estilo SaaS 2024/2025
- Portal do cliente para acompanhamento
- Integração com ERP/RH e eSocial

---


## 1. VISÃO DO PRODUTO

### 1.1 Proposta de Valor

**"Transforme a gestão de SST da sua empresa em uma vantagem competitiva com automação inteligente, conformidade garantida e zero papel."**

O sistema SST SaaS é uma plataforma completa de gestão de Segurança e Saúde do Trabalho desenvolvida especificamente para prestadores de serviços de SST que atendem múltiplas empresas clientes. A solução elimina planilhas, reduz passivos trabalhistas, automatiza conformidade com NRs e eSocial, e oferece visibilidade total sobre pendências e vencimentos.

**Benefícios Mensuráveis:**
- **Redução de 80%** no tempo gasto com processos administrativos de SST
- **Zero rejeições** no eSocial SST com validação prévia inteligente
- **Eliminação de 100%** do papel com assinatura eletrônica e evidências digitais
- **Redução de 90%** em multas e passivos trabalhistas por falta de conformidade
- **ROI em 6 meses** através de ganho de produtividade e redução de custos

### 1.2 Principais Personas

#### Persona 1: Prestador SST (Admin/Owner)
**Nome:** Carlos Silva, 45 anos  
**Cargo:** Proprietário da empresa de consultoria SST  
**Contexto:** Atende 25 empresas clientes (2.500 colaboradores) com equipe de 5 técnicos  
**Dores:**
- Perde controle sobre vencimentos de EPI, ASO e treinamentos
- Não tem visibilidade consolidada de todos os clientes
- Gasta 20h/semana gerando relatórios manuais
- Sofre com retrabalho por rejeições no eSocial
- Dificuldade em escalar a operação sem contratar mais pessoas

**Objetivos:**
- Ter painel consolidado de pendências de todos os clientes
- Automatizar alertas e convocações
- Reduzir tempo administrativo em 80%
- Crescer a carteira sem aumentar proporcionalmente a equipe
- Ter evidências sólidas para auditoria e defesa trabalhista

#### Persona 2: Técnico de Segurança do Trabalho
**Nome:** Juliana Santos, 32 anos  
**Cargo:** Técnica de Segurança do Trabalho  
**Contexto:** Atende 5 clientes, realiza inspeções, entregas de EPI e treinamentos  
**Dores:**
- Dificuldade em acessar informações em campo (sem acesso ao escritório)
- Processo manual de entrega de EPI gera retrabalho (papel, assinatura, arquivo)
- Não sabe quais colaboradores estão com treinamento vencido
- Inspeções registradas em papel e depois digitadas

**Objetivos:**
- Acessar sistema via celular em campo
- Entregar EPI com assinatura eletrônica instantânea
- Ter lista automática de convocados para treinamento
- Registrar inspeções direto no sistema via mobile
- QR Code para acelerar check-in/out de equipamentos

#### Persona 3: RH do Cliente (Empresa Contratante)
**Nome:** Márcia Oliveira, 38 anos  
**Cargo:** Analista de RH Sênior  
**Contexto:** Empresa com 200 colaboradores, contrata prestador SST  
**Dores:**
- Não tem visibilidade sobre pendências de SST da empresa
- Recebe multas por ASO vencido e não sabia
- Dificuldade em obter relatórios para auditorias
- Processo manual de solicitação de exames e documentos

**Objetivos:**
- Portal self-service para acompanhar pendências
- Alertas automáticos de vencimentos
- Download de documentos (ASO, PCMSO, PPP, etc.)
- Solicitar exames e acompanhar status
- Relatórios exportáveis para auditorias

#### Persona 4: Médico do Trabalho
**Nome:** Dr. Roberto Faria, 50 anos  
**Cargo:** Médico do Trabalho (credenciado)  
**Contexto:** Atende convocações de exames ocupacionais  
**Dores:**
- Não recebe histórico completo do colaborador
- Sistema atual não tem prontuário eletrônico
- Emissão manual de ASO (Word/PDF)
- Não há integração com eSocial (S-2220)

**Objetivos:**
- Acesso ao prontuário completo do colaborador
- Emissão de ASO digital com assinatura eletrônica
- Integração automática com eSocial
- Agenda de convocações organizada

#### Persona 5: Almoxarife / Controlador de EPI
**Nome:** José Mendes, 42 anos  
**Cargo:** Almoxarife  
**Contexto:** Controla estoque e entrega de EPIs em empresa de construção  
**Dores:**
- Controle de estoque em planilha Excel
- Não sabe quando CA de EPI vence
- Entrega de EPI manual com ficha de papel
- Dificuldade em fazer inventário (não sabe quem está com o quê)

**Objetivos:**
- Sistema de estoque com entrada/saída automatizada
- Alertas de CA vencido e ruptura de estoque
- Entrega rápida com assinatura eletrônica e foto
- Relatórios de EPI por colaborador/setor
- QR Code para facilitar inventário

#### Persona 6: Auditor / Fiscal do Trabalho
**Nome:** Dr. Fernando Costa, 48 anos  
**Cargo:** Auditor Fiscal do Trabalho  
**Contexto:** Realiza fiscalizações em empresas  
**Expectativas:**
- Evidências sólidas de conformidade
- Trilha de auditoria completa e inalterável
- Acesso rápido a documentos (PCMSO, PGR, LTCAT, PPP)
- Registros de entrega de EPI com assinatura e data
- Comprovação de treinamentos realizados

**O que o sistema deve oferecer:**
- Versionamento de documentos com hash
- Logs imutáveis de todas as ações críticas
- Assinatura eletrônica com IP, timestamp e evidências
- Relatórios de conformidade em tempo real
- Exportação completa de evidências

### 1.3 Principais Dores Resolvidas

#### Dor 1: Falta de Controle sobre Vencimentos
**Problema:** Planilhas desatualizadas levam a ASO, EPI e treinamentos vencidos, gerando multas e passivo trabalhista.  
**Solução:** Motor de alertas inteligente com notificações automáticas 30/15/7 dias antes do vencimento. Dashboard visual de pendências em tempo real.

#### Dor 2: Processo Manual e Burocrático
**Problema:** 80% do tempo gasto em tarefas administrativas (papel, digitação, arquivo).  
**Solução:** Digitalização completa com assinatura eletrônica, automação de workflows e eliminação de papel.

#### Dor 3: Rejeições no eSocial SST
**Problema:** Envios manuais ao eSocial com inconsistências geram rejeições e retrabalho.  
**Solução:** Validação prévia de dados, consistência automática entre PGR/PCMSO/ASO, geração correta de eventos S-2210/S-2220/S-2240.

#### Dor 4: Falta de Evidências para Auditoria
**Problema:** Sem comprovação sólida de entrega de EPI, treinamentos e orientações, empresa fica vulnerável em processos trabalhistas.  
**Solução:** Trilha de auditoria completa, versionamento, assinatura eletrônica com IP/timestamp/dispositivo, anexo de fotos e evidências.

#### Dor 5: Dificuldade de Acesso em Campo
**Problema:** Informações presas no escritório, técnicos precisam voltar para consultar ou registrar dados.  
**Solução:** Interface responsiva mobile-first, QR Code para check-in/out, operação offline com sincronização.

#### Dor 6: Falta de Visibilidade para o Cliente
**Problema:** RH da empresa cliente não sabe o status de SST, depende de ligações e e-mails ao prestador.  
**Solução:** Portal do cliente com dashboard de pendências, download de documentos, solicitações online e acompanhamento em tempo real.

### 1.4 Diferenciais e Posicionamento Competitivo

#### Diferenciais Exclusivos

**1. Automação Inteligente End-to-End**
- Motor de regras configurável para alertas personalizados
- Workflows automatizados (convocação → agendamento → exame → ASO → eSocial)
- Geração automática de documentos (PCMSO, PGR, PPP, LTCAT) baseada em templates

**2. QR Code e Mobilidade Real**
- Cada EPI, equipamento e colaborador tem QR Code único
- Check-in/out instantâneo via celular
- Inspeções e auditorias registradas em campo
- Entrega de EPI com assinatura eletrônica no ato

**3. Assinatura Eletrônica com Força Jurídica**
- Captura de IP, timestamp, dispositivo, geolocalização
- Versão do documento no momento da assinatura (hash SHA-256)
- Opção de biometria facial ou digital (futuro)
- Trilha de auditoria imutável (blockchain-like)
- Validade jurídica conforme MP 2.200-2/2001 e Lei 14.063/2020

**4. eSocial SST Zero Rejeições**
- Validação prévia com regras do leiaute eSocial
- Consistência automática entre módulos (PGR → PCMSO → ASO → eventos)
- Fila de envio com retry automático
- Dashboard de status e erros com sugestões de correção
- Mapeamento inteligente de dados internos para eventos

**5. Portal do Cliente Intuitivo**
- Dashboard visual de pendências por setor/colaborador
- Downloads de documentos em PDF assinado
- Solicitação de exames, treinamentos e documentos online
- Acompanhamento de status em tempo real
- Exportação de relatórios personalizados

**6. Design Moderno e UX de Mercado**
- Interface estilo SaaS 2024/2025 (inspirado em Asana, Monday, Notion)
- Tema claro/escuro
- Sidebar colapsável, breadcrumbs, busca global
- Tabelas com filtros avançados e exportação
- Modais, steppers, wizards para processos complexos
- Responsivo mobile-first

**7. Integrações e Ecossistema**
- API REST para integração com ERP/RH (TOTVS, SAP, Senior)
- Webhooks para eventos críticos
- Importação em lote via CSV/Excel
- Exportação para BI (Power BI, Google Data Studio)
- Integração com WhatsApp/Telegram para notificações

#### Comparativo com Concorrentes

| Funcionalidade | Sistema SST SaaS | Concorrente A | Concorrente B | SOC (Líder) |
|---------------|------------------|--------------|--------------|-------------|
| Multi-tenant nativo | ✅ Sim | ✅ Sim | ⚠️ Parcial | ✅ Sim |
| Assinatura eletrônica com trilha | ✅ Avançada | ⚠️ Básica | ❌ Não | ✅ Sim |
| QR Code para EPI/Equipamentos | ✅ Sim | ❌ Não | ❌ Não | ⚠️ Parcial |
| Portal do cliente | ✅ Completo | ⚠️ Básico | ❌ Não | ✅ Sim |
| eSocial SST integrado | ✅ S-2210/2220/2240 | ⚠️ Apenas S-2220 | ❌ Não | ✅ Completo |
| Mobilidade real (campo) | ✅ Sim | ❌ Não | ❌ Não | ⚠️ Limitada |
| Cautela de equipamentos | ✅ Sim | ❌ Não | ❌ Não | ❌ Não |
| API e integrações | ✅ API REST completa | ⚠️ Limitada | ❌ Não | ✅ Sim |
| Design moderno | ✅ SaaS 2025 | ⚠️ Ultrapassado | ⚠️ Básico | ✅ Moderno |
| Preço (por vida/mês) | R$ 8-12 | R$ 12-18 | R$ 10-15 | R$ 15-25 |

**Legenda:** ✅ Completo | ⚠️ Parcial/Limitado | ❌ Não possui

#### Posicionamento de Mercado

**Segmento-alvo:** Prestadores de serviços de SST (Técnicos, Engenheiros, Médicos do Trabalho) que atendem de 5 a 200 empresas clientes, com 50 a 10.000 colaboradores sob gestão.

**Proposta de valor resumida:**  
*"O único sistema de SST que combina automação inteligente, conformidade garantida e experiência de uso de SaaS moderno, permitindo que prestadores de SST escalem sua operação sem aumentar custos operacionais."*

**Estratégia de entrada:**
1. **Fase 1:** Aquisição de early adopters (prestadores pequenos/médios) com preço competitivo
2. **Fase 2:** Expansão para clientes enterprise via integrações e módulos avançados
3. **Fase 3:** Marketplace de módulos e plugins para customizações

**Diferenciação sustentável:**
- **Tecnologia:** Arquitetura moderna, escalável, com foco em automação e IA (futuro)
- **Domínio:** Conhecimento profundo de SST, NRs e eSocial brasileiro
- **Experiência:** UX/UI de nível SaaS internacional em nicho de SST
- **Ecossistema:** Integrações nativas com principais ERPs e plataformas brasileiras



---

## 2. MÓDULOS E FUNCIONALIDADES

### 2.1 Visão Geral dos Módulos

```
Sistema SST SaaS
├── M01 - Core / Fundação
│   ├── Multi-tenant e Segurança
│   ├── Autenticação e Autorização (RBAC)
│   ├── Auditoria e Logs
│   └── Configurações Globais
├── M02 - Cadastros Base
│   ├── Clientes (Empresas Contratantes)
│   ├── Filiais e Estabelecimentos
│   ├── Setores e Áreas
│   ├── Cargos e Funções
│   ├── GHE (Grupos Homogêneos de Exposição)
│   └── Colaboradores
├── M03 - Gestão de EPI
│   ├── Catálogo de EPIs
│   ├── Certificado de Aprovação (CA)
│   ├── Estoque e Movimentação
│   ├── Entrega e Assinatura
│   ├── Devolução e Troca
│   ├── Ficha de EPI por Colaborador
│   └── Alertas e Relatórios
├── M04 - Cautela de Equipamentos
│   ├── Cadastro de Equipamentos
│   ├── Calibração e Manutenção
│   ├── Empréstimo (Check-out)
│   ├── Devolução (Check-in)
│   ├── Avarias e Ocorrências
│   └── QR Code e Inventário
├── M05 - Saúde Ocupacional
│   ├── PCMSO (Programa)
│   ├── ASO (Atestado de Saúde Ocupacional)
│   ├── Exames Ocupacionais
│   ├── Prontuário Eletrônico
│   ├── Agenda e Convocação
│   ├── Clínicas e Credenciados
│   └── Relatórios e Indicadores
├── M06 - Segurança do Trabalho
│   ├── PGR/GRO (Programa de Gerenciamento de Riscos)
│   ├── Inventário de Riscos
│   ├── Avaliações (Qualitativa/Quantitativa)
│   ├── Medidas de Controle (EPC/EPI)
│   ├── Plano de Ação
│   ├── Inspeções e Auditorias
│   ├── LTCAT e PPP
│   └── CAT (Comunicação de Acidente)
└── M07-M13 - (Demais módulos detalhados no documento completo)
```

### 2.2 Resumo de Priorização MVP

**Fase 0 (Fundação - 4 semanas):**
- M01: Core/Fundação (multi-tenant, RBAC, auditoria)
- M02: Cadastros Base (clientes, filiais, colaboradores)

**Fase 1 (MVP Vendável - 12 semanas):**
- M03: Gestão de EPI (completo com assinatura eletrônica)
- M04: Cautela de Equipamentos (QR Code)
- M05: Saúde Ocupacional (ASO, exames básicos)
- M08: Documentos e Assinaturas
- M10: Portal do Cliente (básico)
- M11: Notificações (e-mail)
- M13: Dashboards e Relatórios

**Fase 2 (Expansão - 8 semanas):**
- M06: PGR completo, LTCAT, PPP
- M07: Treinamentos e Certificados

**Fase 3 (Enterprise - 8 semanas):**
- M09: eSocial SST
- M12: API e Integrações



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

