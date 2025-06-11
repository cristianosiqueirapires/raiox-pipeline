#!/usr/bin/env python3

# Script para corrigir formatação do main.py

with open('/opt/raiox-app/app/main.py', 'r') as f:
    content = f.read()

# Corrigir a linha mal formatada
old_line = '        # Converter array para formato PostgreSQL        vector_str = str(query_vector.tolist()).replace("[", "{").replace("]", "}")                # SQL direto sem parâmetros problemáticos        sql = f"""            SELECT id, name, manufacturer, image_url            FROM implants            ORDER BY embedding <-> "{vector_str}"::vector            LIMIT {limit}        """                with engine.connect() as conn:            result = conn.execute(text(sql))'

new_lines = '''        # Converter array para formato PostgreSQL
        vector_str = str(query_vector.tolist()).replace("[", "{").replace("]", "}")
        
        # SQL direto sem parâmetros problemáticos
        sql = f"""
            SELECT id, name, manufacturer, image_url
            FROM implants
            ORDER BY embedding <-> '{vector_str}'::vector
            LIMIT {limit}
        """
        
        with engine.connect() as conn:
            result = conn.execute(text(sql))'''

content = content.replace(old_line, new_lines)

with open('/opt/raiox-app/app/main.py', 'w') as f:
    f.write(content)

print("Formatação corrigida!")

