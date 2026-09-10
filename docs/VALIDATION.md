# Validation record / Registro de validação

Review date / Data da revisão: 2026-09-10.

## Change and reason / Mudança e motivo

EN: Preserved fractional edge weights; fixed statistics for an explicitly supplied empty graph; added endpoint and weight validation.

PT: Preservados pesos fracionários; corrigidas estatísticas de grafo vazio informado explicitamente; adicionada validação de participantes e pesos.

## Reproduce / Reproduzir

```sh
python -m venv .venv
# Activate .venv for your shell / Ative .venv no seu terminal
python -m pip install -r requirements-validation.txt
python -m pytest -q
python -m examples.review_demo
```

## Example evidence / Evidência do exemplo

4 nodes, 2 edges, 2 connected components; A–B weight = 0.75. / 4 nós, 2 arestas, 2 componentes conexos; peso A–B = 0,75.

EN: The suite includes normal operations and regression cases for the corrected behavior. The example checks values produced by the implementation. Use the linked workflow to inspect the result for a specific commit; no performance benchmark is inferred from a passing build.

PT: A suíte inclui operações válidas e regressões dos comportamentos corrigidos. O exemplo verifica valores produzidos pela implementação. Consulte a automação para conferir o resultado de um commit específico; aprovação de compilação não implica benchmark de desempenho.

## Limits / Limites

EN: The example is synthetic. Network centrality is not a measure of employee worth or productivity. No employee monitoring system or causal inference is demonstrated.

PT: O exemplo é fictício. Centralidade não mede valor ou produtividade de pessoas. O projeto não demonstra um sistema de monitoramento de funcionários nem inferência causal.

[Return to README / Voltar ao README](../README.md)

## Verified suite / Suíte verificada

**76 software tests passed / testes de software aprovados.**

README Mermaid syntax and local documentation links were checked. / A sintaxe Mermaid do README e os links locais da documentação foram conferidos.
