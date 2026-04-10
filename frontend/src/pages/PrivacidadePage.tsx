export function PrivacidadePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-slate-800 py-12 px-4">
      <div className="max-w-3xl mx-auto bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 md:p-12">
        <h1 className="text-3xl font-bold text-slate-800 dark:text-white mb-2">
          Politica de Privacidade
        </h1>
        <p className="text-sm text-slate-500 dark:text-gray-400 mb-8">
          Ultima atualizacao: Abril de 2026
        </p>

        <div className="prose prose-slate dark:prose-invert max-w-none space-y-6 text-slate-600 dark:text-gray-300">
          <section>
            <h2 className="text-xl font-semibold text-slate-800 dark:text-white">
              1. Introducao
            </h2>
            <p>
              O Traduz Saude valoriza sua privacidade e esta comprometido com a protecao
              dos seus dados pessoais em conformidade com a Lei Geral de Protecao de Dados
              (LGPD - Lei 13.709/2018).
            </p>
            <p>
              Esta politica explica como coletamos, usamos, armazenamos e protegemos
              suas informacoes.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-800 dark:text-white">
              2. Dados que Coletamos
            </h2>

            <h3 className="text-lg font-medium text-slate-700 dark:text-gray-200 mt-4">
              2.1 Dados de Cadastro
            </h3>
            <ul className="list-disc pl-6 space-y-2">
              <li>Nome completo</li>
              <li>Email</li>
              <li>Idade e localizacao (cidade/estado)</li>
              <li>Perfil de uso (paciente, cuidador, estudante, etc.)</li>
              <li>Para especialistas: registro profissional (CRM, CRF, etc.)</li>
            </ul>

            <h3 className="text-lg font-medium text-slate-700 dark:text-gray-200 mt-4">
              2.2 Dados de Documentos
            </h3>
            <p>
              Quando voce envia um laudo ou receita para traducao:
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li>
                <strong>Anonimizacao automatica:</strong> Nomes, CPF, datas de nascimento
                e outros dados pessoais sao removidos ANTES do processamento pela IA
              </li>
              <li>O texto anonimizado e enviado para processamento</li>
              <li>Voce pode optar por salvar ou nao o historico de traducoes</li>
            </ul>

            <h3 className="text-lg font-medium text-slate-700 dark:text-gray-200 mt-4">
              2.3 Dados Epidemiologicos (Opcional)
            </h3>
            <p>
              Com seu consentimento, podemos coletar dados anonimizados e agregados para
              fins de pesquisa epidemiologica:
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Categoria de condicao medica (ex: cardiovascular, respiratorio)</li>
              <li>Faixa etaria (nao idade exata)</li>
              <li>Regiao geografica (municipio/estado)</li>
            </ul>
            <p className="text-sm italic">
              Esses dados sao completamente anonimizados e agregados, seguindo o principio
              de k-anonimidade para garantir que nenhum individuo possa ser identificado.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-800 dark:text-white">
              3. Como Usamos Seus Dados
            </h2>
            <ul className="list-disc pl-6 space-y-2">
              <li>
                <strong>Fornecer o servico:</strong> Traduzir seus documentos medicos
              </li>
              <li>
                <strong>Manter seu historico:</strong> Se voce optar por salvar traducoes
              </li>
              <li>
                <strong>Melhorar o servico:</strong> Analisar padroes de uso anonimizados
              </li>
              <li>
                <strong>Pesquisa epidemiologica:</strong> Apenas com seu consentimento explicito
              </li>
              <li>
                <strong>Comunicacao:</strong> Enviar atualizacoes importantes sobre o servico
              </li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-800 dark:text-white">
              4. Processamento por IA
            </h2>
            <p>
              Utilizamos servicos de inteligencia artificial de terceiros para processar
              as traducoes:
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Anthropic (Claude)</li>
              <li>OpenAI (GPT)</li>
              <li>Google (Gemini)</li>
            </ul>
            <p>
              <strong>Importante:</strong> Apenas dados ja anonimizados sao enviados para
              esses servicos. Nenhum dado pessoal identificavel e compartilhado com
              provedores de IA.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-800 dark:text-white">
              5. Armazenamento e Seguranca
            </h2>
            <ul className="list-disc pl-6 space-y-2">
              <li>Dados sao armazenados em servidores seguros</li>
              <li>Criptografia em transito (HTTPS) e em repouso</li>
              <li>Acesso restrito apenas a pessoal autorizado</li>
              <li>Backups regulares e protegidos</li>
              <li>Monitoramento de seguranca continuo</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-800 dark:text-white">
              6. Seus Direitos (LGPD)
            </h2>
            <p>Conforme a LGPD, voce tem direito a:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>
                <strong>Acesso:</strong> Solicitar uma copia dos seus dados
              </li>
              <li>
                <strong>Correcao:</strong> Corrigir dados incorretos ou incompletos
              </li>
              <li>
                <strong>Exclusao:</strong> Solicitar a exclusao dos seus dados
              </li>
              <li>
                <strong>Portabilidade:</strong> Receber seus dados em formato estruturado
              </li>
              <li>
                <strong>Revogacao:</strong> Retirar consentimentos dados anteriormente
              </li>
              <li>
                <strong>Informacao:</strong> Saber com quem seus dados foram compartilhados
              </li>
            </ul>
            <p>
              Para exercer esses direitos, entre em contato pelo email:
              <a
                href="mailto:privacidade@traduzsaude.com.br"
                className="text-blue-600 hover:text-blue-700 dark:text-blue-400 ml-1"
              >
                privacidade@traduzsaude.com.br
              </a>
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-800 dark:text-white">
              7. Cookies e Tecnologias Similares
            </h2>
            <p>Utilizamos cookies essenciais para:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Manter sua sessao de login</li>
              <li>Lembrar suas preferencias</li>
              <li>Garantir a seguranca da plataforma</li>
            </ul>
            <p>
              Nao utilizamos cookies de rastreamento ou publicidade.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-800 dark:text-white">
              8. Retencao de Dados
            </h2>
            <ul className="list-disc pl-6 space-y-2">
              <li>
                <strong>Dados de conta:</strong> Mantidos enquanto sua conta estiver ativa
              </li>
              <li>
                <strong>Historico de traducoes:</strong> Conforme sua preferencia, pode ser excluido a qualquer momento
              </li>
              <li>
                <strong>Dados epidemiologicos:</strong> Mantidos de forma anonimizada e agregada indefinidamente para fins de pesquisa
              </li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-800 dark:text-white">
              9. Menores de Idade
            </h2>
            <p>
              O Traduz Saude nao e destinado a menores de 18 anos. Se voce e responsavel
              por um menor e deseja usar o servico em seu nome, voce assume a responsabilidade
              pelo uso.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-800 dark:text-white">
              10. Alteracoes nesta Politica
            </h2>
            <p>
              Podemos atualizar esta politica periodicamente. Alteracoes significativas
              serao comunicadas por email ou notificacao na plataforma com pelo menos
              30 dias de antecedencia.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-800 dark:text-white">
              11. Contato e DPO
            </h2>
            <p>
              Para questoes sobre privacidade e protecao de dados:
            </p>
            <p>
              <strong>Email:</strong>{' '}
              <a
                href="mailto:privacidade@traduzsaude.com.br"
                className="text-blue-600 hover:text-blue-700 dark:text-blue-400"
              >
                privacidade@traduzsaude.com.br
              </a>
            </p>
          </section>
        </div>

        <div className="mt-10 pt-6 border-t border-slate-200 dark:border-gray-700">
          <a
            href="/"
            className="inline-flex items-center text-blue-600 hover:text-blue-700 dark:text-blue-400 font-semibold"
          >
            &larr; Voltar para a pagina inicial
          </a>
        </div>
      </div>
    </div>
  )
}
