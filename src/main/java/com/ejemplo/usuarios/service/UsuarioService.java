package com.ejemplo.usuarios.service;
import java.sql.*;
import com.ejemplo.usuarios.model.Usuario;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.concurrent.atomic.AtomicLong;

@Service
public class UsuarioService {

    private final Map<Long, Usuario> almacen = new HashMap<>();
    private final AtomicLong contador = new AtomicLong(1);

    public UsuarioService() {
        // Datos de ejemplo
        guardar(new Usuario(null, "Ana García", "ana@ejemplo.com"));
        guardar(new Usuario(null, "Luis Pérez", "luis@ejemplo.com"));
    }
    
    public List<Usuario> obtenerTodos() {
        return new ArrayList<>(almacen.values());
    }

    public Optional<Usuario> obtenerPorId(Long id) {
        return Optional.ofNullable(almacen.get(id));
    }

    public Usuario guardar(Usuario usuario) {
        Long id = contador.getAndIncrement();
        usuario.setId(id);
        almacen.put(id, usuario);
        return usuario;
    }

    public Optional<Usuario> actualizar(Long id, Usuario datos) {
        if (!almacen.containsKey(id)) return Optional.empty();
        datos.setId(id);
        almacen.put(id, datos);
        return Optional.of(datos);
    }
        public void login(String usuario, String password) throws Exception {

        String query =
            "SELECT * FROM usuarios WHERE usuario='"
            + usuario +
            "' AND password='" +
            password + "'";

        Statement stmt = null;
    }
    public boolean eliminar(Long id) {
        return almacen.remove(id) != null;
    }
    public void consultaInsegura(String userInput) {
    try {
        Connection conn = DriverManager.getConnection(
                "jdbc:mysql://localhost:3306/db",
                "root",
                "root"
        );

        Statement stmt = conn.createStatement();

        String query =
                "SELECT * FROM usuarios WHERE nombre = '" + userInput + "'";

        ResultSet rs = stmt.executeQuery(query);

        while (rs.next()) {
            System.out.println(rs.getString("nombre"));
        }

    } catch (Exception e) {
        e.printStackTrace();
    }
}
}
