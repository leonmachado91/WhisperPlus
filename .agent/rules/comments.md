---
trigger: always_on
glob:
description: Comentários no Formato Obsidian
---

Sempre interprete sessões com esse formato como comentários do usuário:

```
%% comentário aqui %%
```

## Interpretação

Quando encontrar esse padrão:

1. **Contexto**: O comentário se refere à seção/parágrafo imediatamente anterior ou ao trecho onde está inserido
2. **Ação**: Tratar como instrução do usuário — pode ser uma correção, pergunta, pedido de expansão, ou observação
3. **Resposta**: Ao processar o arquivo, identificar todos os `%% %%` e endereçar cada um

## Prioridade

Se houver múltiplos comentários, processar na ordem em que aparecem.