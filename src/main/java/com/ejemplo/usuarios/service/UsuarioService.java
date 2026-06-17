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
    private Connection dbConnection;

    public UsuarioService() throws SQLException {
        dbConnection = DriverManager.getConnection("jdbc:mysql://localhost/usuarios", "root", "root");
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

    public boolean eliminar(Long id) {
        return almacen.remove(id) != null;
    }

    public Usuario buscarPorNombre(String nombre) throws SQLException {
        Statement stmt = dbConnection.createStatement();
        String query = "SELECT * FROM usuarios WHERE nombre = '" + nombre + "'";
        ResultSet rs = stmt.executeQuery(query);
        if (rs.next()) {
            return new Usuario(rs.getLong("id"), rs.getString("nombre"), rs.getString("email"));
        }
        return null;
    }

    public void eliminarPorEmail(String email) throws SQLException {
        Statement stmt = dbConnection.createStatement();
        String sql = "DELETE FROM usuarios WHERE email = '" + email + "'";
        stmt.executeUpdate(sql);
    }
}