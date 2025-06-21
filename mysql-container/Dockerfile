# NOTE: AWS RDS の MySQL バージョンに合わせています。
FROM mysql:8.0

# NOTE: 8.0 から default collation が utf8mb4_0900_ai_ci です。
#       日本語の collation として曖昧さが目立つので変更しています。
# WARN: RUN だとエラーになります。
# NOTE: CMD は主要な実行プロセスを指定します。
CMD [ "mysqld", "--collation-server=utf8mb4_general_ci" ]

# NOTE: このポートを解放する意図である、というドキュメントとして機能するコマンドです。
#       ポートを実際に解放するコマンドではありません。
EXPOSE 3306
