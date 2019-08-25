class _SQLMarcador(object):

    QryGetAttendance =  """
                        SELECT dni, fecha, hora, maquina
                          FROM attendance
                          WHERE fecha
                          BETWEEN DATE_SUB(NOW(), INTERVAL 7 DAY) AND NOW()
                          GROUP BY dni,fecha,hora
                          ORDER BY fecha ASC, dni ASC
                        """
