export function TermosPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-slate-800 py-12 px-4">
      <div className="max-w-3xl mx-auto bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 md:p-12">
        <h1 className="text-3xl font-bold text-slate-800 dark:text-white mb-2">
          Termos de Uso
        </h1>
        <p className="text-sm text-slate-500 dark:text-gray-400 mb-8">
          Ultima atualizacao: Abril de 2026
        </p>

        <div className="prose prose-slate dark:prose-invert max-w-none space-y-6 text-slate-600 dark:text-gray-300">
          <section>
            <h2 className="text-xl font-semibold text-slate-800 dark:text-white">
              1. Sobre o Traduz Saude
            </h2>
            <p>
              O Traduz Saude e uma plataforma que utiliza inteligencia artificial para traduzir
              documentos medicos (laudos, exames, receitas) de linguagem tecnica para uma
              linguagem acessivel e compreensivel ao paciente.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-800 dark:text-white">
              2. Importante: Nao Substitui Consulta Medica
            </h2>
            <p className="font-semibold text-red-600 dark:text-red-400">
              Este servico NAO substitui consulta medica, diagnostico ou tratamento profissional.
            </p>
            <p>
              As traducoes sao apenas para fins educativos e de compreensao. Sempre consulte
              um profissional de saude qualificado para interpretar seus exames e tomar
              decisoes sobre seu tratamento.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-800 dark:text-white">
              3. Uso da Inteligencia Artificial
            </h2>
            <p>
              Utilizamos modelos de IA (como Claude da Anthropic, GPT da OpenAI e Gemini do Google)
              para processar e traduzir os documentos. Embora essas tecnologias sejam avancadas,
              podem ocorrer imprecisoes ou erros nas traducoes.
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li>As traducoes sao geradas automaticamente por IA</li>
              <li>Revisoes por especialistas podem estar disponiveis para validacao</li>
              <li>Nao garantimos 100% de precisao nas traducoes</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-800 dark:text-white">
              4. Privacidade e Protecao de Dados
            </h2>
            <p>
              Nos comprometemos com a protecao dos seus dados conforme a Lei Geral de
              Protecao de Dados (LGPD - Lei 13.709/2018):
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Dados pessoais (nomes, CPF, datas) sao automaticamente anonimizados antes do processamento</li>
              <li>Voce pode optar por nao contribuir com dados para pesquisa epidemiologica</li>
              <li>Seus documentos sao criptografados e protegidos</li>
              <li>Consulte nossa Politica de Privacidade para mais detalhes</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-800 dark:text-white">
              5. Conta de Especialista
            </h2>
            <p>
              Profissionais de saude podem solicitar uma conta de especialista para:
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Revisar e validar traducoes</li>
              <li>Fornecer feedback tecnico sobre a qualidade das traducoes</li>
              <li>Contribuir para a melhoria do sistema</li>
            </ul>
            <p>
              O cadastro de especialista requer verificacao do registro profissional
              (CRM, CRF, COREN, etc.) e pode estar sujeito a aprovacao.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-800 dark:text-white">
              6. Uso Aceitavel
            </h2>
            <p>Ao usar o Traduz Saude, voce concorda em:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Usar o servico apenas para fins legitimos e pessoais</li>
              <li>Nao tentar burlar os sistemas de seguranca</li>
              <li>Nao usar as traducoes para fins comerciais sem autorizacao</li>
              <li>Respeitar os direitos de propriedade intelectual</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-800 dark:text-white">
              7. Limitacao de Responsabilidade
            </h2>
            <p>
              O Traduz Saude e fornecido "como esta", sem garantias de qualquer tipo.
              Nao nos responsabilizamos por:
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Decisoes medicas tomadas com base nas traducoes</li>
              <li>Imprecisoes ou erros nas traducoes geradas por IA</li>
              <li>Indisponibilidade temporaria do servico</li>
              <li>Perda de dados em circunstancias excepcionais</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-800 dark:text-white">
              8. Alteracoes nos Termos
            </h2>
            <p>
              Podemos atualizar estes termos periodicamente. Alteracoes significativas
              serao comunicadas por email ou notificacao na plataforma.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-slate-800 dark:text-white">
              9. Contato
            </h2>
            <p>
              Duvidas sobre estes termos? Entre em contato:
              <br />
              <a
                href="mailto:contato@traduzsaude.com.br"
                className="text-blue-600 hover:text-blue-700 dark:text-blue-400"
              >
                contato@traduzsaude.com.br
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
