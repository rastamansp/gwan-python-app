## DOCUMENTO DE ARQUITETURA DE SOLUÇÃO

GAL Externa no Copilot

<!-- image -->

<!-- image -->

## DOCUMENTO DE

## ARQUITETURA DA SOLUÇÃO

Projeto:

| GAL via Teams                      | GAL via Teams   |
|------------------------------------|-----------------|
| Desenvolvido Por:                  | Data:           |
| Pedro Henrique Pinheiro de Almeida | 30/10/2024      |
| Solicitante:                       | Páginas:        |
| Joyce dos Santos Caetano           | Página 2 de 13  |

## SUMÁRIO

| 1.   | OBJETIVO.................................................................................................................................4   |
|------|----------------------------------------------------------------------------------------------------------------------------------------------|
| 2.   | SOLUÇÕES...............................................................................................................................5     |
|      | 2.1. Arquitetura da Solução ......................................................................................................5          |
|      | 2.2. Considerações de Arquitetura ...........................................................................................8               |
| 3.   | CHECKLIST...............................................................................................................................9    |
|      | 3.1. Tecnologia..........................................................................................................................9   |
|      | 3.2. Integração ........................................................................................................................10   |
|      | 3.3. Segurança........................................................................................................................11     |
|      | 3.4. Infraestrutura....................................................................................................................11    |
|      | 3.5. Disponibilidade.................................................................................................................12      |
|      | 3.6. Eficiência..........................................................................................................................12  |
|      | 3.7. Manutenibilidade..............................................................................................................12        |
|      | 3.8. Usabilidade ......................................................................................................................12    |
|      | 3.9. Go Live.............................................................................................................................13  |

<!-- image -->

Projeto:

GAL via Teams

Desenvolvido Por:

Pedro Henrique Pinheiro de Almeida

Data:

30/10/2024

Solicitante:

Joyce dos Santos Caetano

Páginas:

Página 3 de 13

## CONTROLE DE REVISÃO

|   Revisão | Data       | Autor                        | Descrição da Modificação         |
|-----------|------------|------------------------------|----------------------------------|
|         1 | 30/10/2024 | Pedro Henrique P. de Almeida | Elaboração do documento.         |
|         2 | 18/11/2024 | Pedro Henrique P. de Almeida | Atualização Fase 1 do documento. |

## VISÃO DO PROCESSO   ARQUITETURA DA SOLUÇÃO -

<!-- image -->

A sequência de atividades contribui para a qualidade da solução.

## DOCUMENTO DE ARQUITETURA DA SOLUÇÃO

<!-- image -->

## DOCUMENTO DE ARQUITETURA DA SOLUÇÃO

Projeto:

GAL via Teams

Desenvolvido Por:

Pedro Henrique Pinheiro de Almeida

Data:

30/10/2024

Solicitante:

Joyce dos Santos Caetano

Páginas:

Página 4 de 13

## 1. OBJETIVO

O  "AVI  GAL  Atendimento"  é  uma  solução  orientada  à  inovação  e  à  melhoria contínua dos processos de atendimento ao cliente da GOL. Ao integrar tecnologias de IA Generativa e computação em nuvem, a iniciativa se alinha com os objetivos estratégicos da empresa, melhorando a eficiência operacional e promovendo uma experiência de cliente aprimorada e diferenciada.

<!-- image -->

## DOCUMENTO DE

## ARQUITETURA DA SOLUÇÃO

Projeto:

GAL via Teams

Desenvolvido Por:

Pedro Henrique Pinheiro de Almeida

Data:

30/10/2024

Solicitante:

Joyce dos Santos Caetano

Páginas:

Página 5 de 13

## 2. SOLUÇÕES

## 2.1. Arquitetura da Solução

Figura 1: POC Atendimento Copilot

<!-- image -->

<!-- image -->

## DOCUMENTO DE ARQUITETURA DA SOLUÇÃO

Projeto:

GAL via Teams

Desenvolvido Por:

Pedro Henrique Pinheiro de Almeida

Data:

30/10/2024

Solicitante:

Joyce dos Santos Caetano

Páginas:

Página 6 de 13

## 2.2. Requisitos Técnicos

- 1. Infraestrutura e Ambiente de Execução

## Copilot Studio:

- · O Copilot Studio será a plataforma principal para configurar o bot e gerenciar a interaçãocom os clientes.

## Azure App Service:

- · Utilizado para hospedar o middleware, responsável pela comunicação segura entre o Copilot e as APIs da Gol (como Consulta de Voos e Programa Smiles).

## Azure API Management:

- · Se necessário, será utilizado para gerenciar o acesso às APIs da Gol de forma segura, aplicando políticas de segurança e autenticação.

## Azure Monitor &amp; Application Insights:

- · Ferramentas de monitoramento para rastreamento de logs, telemetria e performance das chamadas ao middleware e às APIs.
- 2. Integração com APIs

## APIs da Gol (Consulta de Voos e Smiles):

- · A integração com as APIs de consulta de voos e Programa Smiles requer que o middleware manipule autenticações, como troca de tokens, e formatação das respostas para o Copilot.

Middleware: Será necessário desenvolver um middleware customizado que atuará como

- · intermediário entre o Copilot e as APIs da Gol, cuidando da segurança, formatação de dados e gestão de tokens.
- 3. Monitoramento e Governança

## Azure Application Insights:

- · Para rastreamento de logs e erros, Application Insights será utilizado para monitorar a performance das APIs e o middleware.

## Microsoft Compliance Center:

- · Para garantir conformidade com regulamentações como LGPD, o Compliance Center permitirá definir políticas de retenção e auditoria de dados sensíveis.

<!-- image -->

## DOCUMENTO DE ARQUITETURA DA SOLUÇÃO

Projeto:

GAL via Teams

Desenvolvido Por:

Pedro Henrique Pinheiro de Almeida

Data:

30/10/2024

Solicitante:

Joyce dos Santos Caetano

Páginas:

Página 7 de 13

## 4. Requisitos e Licenças

## Infraestrutura:

- · Power Platform (Copilot Studio)
- · Azure App Service (Middleware)
- · Azure API Management (opcional)
- · Azure Monitor &amp; Application Insights

## Licenças:

- · Copilot Studio;
- · WebApp;

## Uso:

- · Configuração do bot de atendimento no Copilot Studio;
- · Integração com APIs por meio de middleware no Azure;
- · Monitoramento, governança e segurança gerenciados via Azure e Power Platform Admin center.

## 2.3. Entregáveis por Fase

- · Fase 1 : Bot configurado com base de conhecimento existente, usando IA Generativa NLP para fornecer respostas automáticas.
- · Fase 2 : Middleware desenvolvido e integrado com a API de consulta de voos, com monitoramento básico ativo.
- · Fase 3 (Final): Middleware expandido com suporte completo à troca de tokens e autenticação para o Programa Smiles, garantindo conformidade e segurança.

## 2.4. Deployment

## Implantação ocorrerá nos seguintes moldes:

- · Configuração e exportação da solução
- · Acompanhamento da implantação nos ambientes

<!-- image -->

## DOCUMENTO DE ARQUITETURA DA SOLUÇÃO

Projeto:

GAL via Teams

Desenvolvido Por:

Pedro Henrique Pinheiro de Almeida

Data:

30/10/2024

Solicitante:

Joyce dos Santos Caetano

Páginas:

Página 8 de 13

## 2.5. Considerações de Arquitetura

## Para Líder Técnico de Infraestrutura:

- · Providenciar  as  configurações  e  conectividade  necessárias,  considerando todos os requisitos desta solução em ambientes de DEV, HOM e PRD na Azure .
- · Definir estratégia de  implementação  desta  solução  em  ambiente  de produção.

## Para Analista de Negócios TI:

- · Azure DevOps (GIT):
- o Solicitar a criação de repositório e pipeline..
- · Consumo de Disco:
- o N/A.
- · Plano de Mudança:
- o Documentar a implantação da solução com as mudanças informativas conforme processo.
- · Estimativa de Crescimento de Banco de Dados:
- o Informar ao Líder Técnico de Infraestrutura..
- · Outros:
- o N/A.

<!-- image -->

## DOCUMENTO DE ARQUITETURA DA SOLUÇÃO

Projeto:

GAL via Teams

Desenvolvido Por:

Pedro Henrique Pinheiro de Almeida

Data:

30/10/2024

Solicitante:

Joyce dos Santos Caetano

Páginas:

Página 9 de 13

## 3. CHECKLIST

Infraestrutura e Ambiente de Execução

## Copilot Studio:

- · O Copilot Studio será a plataforma principal para configurar o bot e gerenciar a interação com os clientes.

Pod WebApp:

- · Utilizado para hospedar o middleware, interface gráfica responsável pela comunicação segura entre o Copilot e usuário.

## 3.1. Tecnologia

Aquisição de novo produto de mercado

Sim (especificar).

- · Copilot Studio
- · Azure WebApp

Nova Aplicação Web

Sim (especificar).

- · Azure Web App

Nova Aplicação Desktop

N/A.

Novo Banco de Dados

N/A.

Novo WebService

N/A.

Novo Relatório/Dashboard/BI

N/A.

Tecnologia das Interfaces/Orquestrações

Sim (especificar).

- · AKS (Azure Kubernetes Service)

Tecnologia dos Processos de Batch

N/A.

Repositório do GIT

Novo repositório (informar).

<!-- image -->

## DOCUMENTO DE ARQUITETURA DA SOLUÇÃO

Projeto:

GAL via Teams

Desenvolvido Por:

Pedro Henrique Pinheiro de Almeida

Data:

30/10/2024

Solicitante:

Joyce dos Santos Caetano

Páginas:

Página 10 de 13

## 3.2. Integração

Integração com sistemas da Gol N/A.

<!-- image -->

Projeto:

GAL via Teams

Desenvolvido Por:

Pedro Henrique Pinheiro de Almeida

Data:

30/10/2024

Solicitante:

Joyce dos Santos Caetano

Páginas:

Página 11 de 13

## Integração com sistemas externos à Gol

Sim (especificar).

- o Microsoft Copilot Studio

Novos serviços reutilizáveis no barramento SOA N/A.

Consome serviços já existentes do barramento SOA N/A.

## 3.3. Segurança

Autenticação (quem é o usuário)

Integrada com AD (criar usuário de serviço).

Autorização (o que o usuário pode fazer no sistema) Perfís definidos como Grupos do AD (Criar grupos no AD)

Trafega dados pela Internet

Sim, dados sensíveis (requer HTTPS)

Tipo de acesso ao sistema

Liberado para toda a internet (Verificar vulnerabilidade de ataques).

## O usuário é redirecionado entre sites

Não.

## 3.4. Infraestrutura

Data Center que hospeda o novo sistema

N/A

o Azure

Novo link entre datacenters

N/A

Novos servidores no ambiente

N/A.

Instalação em Desktops

N/A.

## DOCUMENTO DE ARQUITETURA DA SOLUÇÃO

<!-- image -->

## DOCUMENTO DE ARQUITETURA DA SOLUÇÃO

Projeto:

GAL via Teams

Desenvolvido Por:

Pedro Henrique Pinheiro de Almeida

Data:

30/10/2024

Solicitante:

Joyce dos Santos Caetano

Páginas:

Página 12 de 13

## E-mails

N/A.

Impressoras

N/A.

## Descrição dos Ambientes

- · Detalhes do ambiente no item 2.2.

## 3.5. Disponibilidade

## Alta disponibilidade (tolerância a falhas)

Cluster ativo-ativo (equipamentos que funcionam como um, com balanceamento).

Contingência (plano B em caso de desastre)

Processo manual (especificar).

Requer Monitoração da Aplicação pela equipe Gol?

Não, pois a monitoração padrão já atende.

## 3.6. Eficiência

Requer Stress Test?

N/A

Utiliza HTTP Compression?

N/A.

Aumento significativo no tráfego MPLS?

N/A

## 3.7. Manutenibilidade

## Dados antigos

N/A.

## 3.8. Usabilidade

## Suporte a Multi-Idiomas

Suporta mais de um idioma no mesmo sistema.

<!-- image -->

## DOCUMENTO DE ARQUITETURA DA SOLUÇÃO

Projeto:

GAL via Teams

Desenvolvido Por:

Pedro Henrique Pinheiro de Almeida

Data:

30/10/2024

Solicitante:

Joyce dos Santos Caetano

Páginas:

Página 13 de 13

## 3.9. Go Live

Estratégia de Cutover N/A.

Migração de Dados

N/A.