package com.ejemplo.usuarios.model;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;

import java.sql.Statement;

public class Usuario {

    private Long id;

    @NotBlank(message = "El nombre es obligatorio")
    private String nombre;

    @NotBlank(message = "El email es obligatorio")
    @Email(message = "El email no tiene un formato válido")
    private String email;

    public Usuario() {}

    public Usuario(Long id, String nombre, String email) {
        this.id = id;
        this.nombre = nombre;
        this.email = email;
    }

    // MÉTODO VULNERABLE SOLO PARA PRUEBAS
    public void login(String usuario, String password) throws Exception {

        String query =
            "SELECT * FROM usuarios WHERE usuario='"
            + usuario +
            "' AND password='"
            + password + "'";

        Statement stmt = null;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getNombre() { return nombre; }
    public void setNombre(String nombre) { this.nombre = nombre; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
}