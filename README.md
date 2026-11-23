# TaskFlow — Flask + Supabase + Vercel

Gerenciador de tarefas didático. Localmente usa SQLite; quando `SUPABASE_URL` e `SUPABASE_SERVICE_ROLE_KEY` estão configuradas, usa Supabase PostgreSQL.

## Rodar localmente

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Abra http://127.0.0.1:5000.

## Preparar o Supabase

1. Crie um projeto em https://supabase.com.
2. Abra SQL Editor e execute o conteúdo de `supabase/schema.sql`.
3. Em Project Settings / API, copie Project URL e a chave `service_role` (secret).
4. Guarde os dois valores para cadastrar como variáveis de ambiente na Vercel.

**Segurança:** `service_role` é uma chave secreta que ignora RLS. Ela deve ficar somente no servidor, como variável de ambiente protegida. Nunca coloque essa chave em JavaScript, HTML, repositório Git ou em variável `NEXT_PUBLIC_`/`VITE_`. Este projeto didático ainda não tem login: as rotas do Flask ficam publicamente acessíveis e todos os visitantes podem manipular a mesma lista. Adicione autenticação e autorização por usuário antes de usar com dados reais.

## Publicar na Vercel

1. Envie o conteúdo desta pasta para um repositório GitHub.
2. Na Vercel, escolha Add New → Project e importe o repositório.
3. Não configure Build Command nem Output Directory; a Vercel detecta Flask pelo `app.py` e `requirements.txt`.
4. Em Project → Settings → Environment Variables, adicione:
   - `SUPABASE_URL` = Project URL do Supabase
   - `SUPABASE_SERVICE_ROLE_KEY` = chave secreta `service_role`
5. Faça Deploy. Se as variáveis forem adicionadas depois do deploy, faça um novo redeploy.

## Observações

- SQLite é usado apenas no desenvolvimento local. O disco das funções Vercel não é armazenamento persistente.
- Não compartilhe a chave `service_role` nem a publique no GitHub.
- Confira os limites atuais dos planos gratuitos da Vercel e Supabase antes de usar em produção.
