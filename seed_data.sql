-- ==========================================
-- SEED: APP USERS
-- ==========================================

INSERT INTO app_users (
    user_id,
    role
)
VALUES
    ('bruno.solver@empresa.com', 'solver'),
    ('carla.solver@empresa.com', 'solver')
ON CONFLICT (user_id) DO NOTHING;


-- ==========================================
-- SEED: TICKETS
-- ==========================================

INSERT INTO tickets (
    ticket_id,
    title,
    status,
    created_by,
    assigned_to,
    created_at,
    resolved_at
)
VALUES
(
    1,
    'Erro ao acessar o sistema',
    'open',
    'ana.cliente@gmail.com',
    NULL,
    '2026-08-01 09:15:00-03',
    NULL
),
(
    2,
    'Falha na integração com API',
    'in_progress',
    'pedro.cliente@gmail.com',
    'bruno.solver@empresa.com',
    '2026-08-02 10:30:00-03',
    NULL
),
(
    3,
    'Dashboard apresentando dados incorretos',
    'resolved',
    'mariana.cliente@gmail.com',
    'carla.solver@empresa.com',
    '2026-08-03 14:45:00-03',
    '2026-08-04 11:20:00-03'
),
(
    4,
    'Solicitação de novo acesso',
    'open',
    'joao.cliente@gmail.com',
    NULL,
    '2026-08-05 08:00:00-03',
    NULL
),
(
    5,
    'Erro ao exportar relatório',
    'in_progress',
    'fernanda.cliente@gmail.com',
    'bruno.solver@empresa.com',
    '2026-08-06 15:30:00-03',
    NULL
)
ON CONFLICT (ticket_id) DO NOTHING;


-- ==========================================
-- SEED: TICKET MESSAGES
-- ==========================================

INSERT INTO ticket_messages (
    ticket_id,
    message_text,
    author,
    created_at
)
VALUES
(
    1,
    'Estou tentando acessar o sistema, mas recebo erro de autenticação.',
    'ana.cliente@gmail.com',
    '2026-08-01 09:20:00-03'
),
(
    1,
    'Recebemos sua solicitação. Vamos analisar o problema.',
    'bruno.solver@empresa.com',
    '2026-08-01 10:00:00-03'
),
(
    2,
    'A integração começou a falhar após a atualização de ontem.',
    'pedro.cliente@gmail.com',
    '2026-08-02 10:35:00-03'
),
(
    2,
    'Identificamos uma alteração na API externa. Estamos corrigindo.',
    'bruno.solver@empresa.com',
    '2026-08-02 13:10:00-03'
),
(
    3,
    'O dashboard está mostrando valores diferentes dos relatórios exportados.',
    'mariana.cliente@gmail.com',
    '2026-08-03 14:50:00-03'
),
(
    3,
    'Os valores do dashboard foram corrigidos.',
    'carla.solver@empresa.com',
    '2026-08-04 11:25:00-03'
),
(
    4,
    'Preciso de acesso ao módulo financeiro.',
    'joao.cliente@gmail.com',
    '2026-08-05 08:10:00-03'
),
(
    4,
    'Recebemos sua solicitação. Qual é o nível de acesso necessário?',
    'carla.solver@empresa.com',
    '2026-08-05 09:30:00-03'
),
(
    5,
    'O relatório não termina a exportação.',
    'fernanda.cliente@gmail.com',
    '2026-08-06 15:40:00-03'
),
(
    5,
    'Estamos investigando o problema. Qual formato de exportação você está usando?',
    'bruno.solver@empresa.com',
    '2026-08-06 16:15:00-03'
)
ON CONFLICT (message_id) DO NOTHING;