// Configuración de la URL base de tu backend en Render (Cambiar por tu URL real de Render cuando la tengas)
const API_BASE_URL = "https://secure-devops-pipeline-1.onrender.com";

// Elementos del DOM
const statusIndicator = document.getElementById("status-indicator");
const userForm = document.getElementById("user-form");
const usersTableBody = document.querySelector("#users-table tbody");
const formMessage = document.getElementById("form-message");

// --- 1. FUNCIÓN PARA VERIFICAR EL ESTADO DEL SISTEMA (GET /health) ---
async function checkSystemHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        
        if (response.ok) {
            // Asumimos que la respuesta exitosa o texto contiene "OK"
            statusIndicator.textContent = "Sistema Operativo";
            statusIndicator.className = "status-badge status-ok";
        } else {
            throw new Error("Respuesta de salud no es OK");
        }
    } catch (error) {
        console.error("Error al consultar /health:", error);
        statusIndicator.textContent = "Sistema No Disponible";
        statusIndicator.className = "status-badge status-error";
    }
}

// --- 2. FUNCIÓN PARA OBTENER Y LISTAR USUARIOS (GET /usuarios) ---
async function fetchUsuarios() {
    try {
        const response = await fetch(`${API_BASE_URL}/usuarios`);
        if (!response.ok) throw new Error("Error al obtener usuarios");

        const usuarios = await response.json();
        
        // Limpiamos la tabla
        usersTableBody.innerHTML = "";

        if (usuarios.length === 0) {
            usersTableBody.innerHTML = `<tr><td colspan="2" class="text-center">No hay usuarios registrados.</td></tr>`;
            return;
        }

        // Insertar cada usuario en la tabla
        usuarios.forEach(usuario => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${escapeHTML(usuario.nombre)}</td>
                <td>${escapeHTML(usuario.email)}</td>
            `;
            usersTableBody.appendChild(row);
        });

    } catch (error) {
        console.error("Error en fetchUsuarios:", error);
        usersTableBody.innerHTML = `<tr><td colspan="2" class="text-center" style="color: red;">Error al conectar con la base de datos de usuarios.</td></tr>`;
    }
}

// --- 3. FUNCIÓN PARA REGISTRAR UN USUARIO (POST /usuarios) ---
userForm.addEventListener("submit", async (e) => {
    e.preventDefault(); // Evita que la página se recargue

    // Capturar datos del formulario
    const nombre = document.getElementById("nombre").value.trim();
    const email = document.getElementById("email").value.trim();

    // Crear el objeto que espera tu controlador Java
    const nuevoUsuario = {
        nombre: nombre,
        email: email
    };

    // Ocultar mensaje previo
    showMessage("", false);

    try {
        const response = await fetch(`${API_BASE_URL}/usuarios`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(nuevoUsuario)
        });

        if (response.ok || response.status === 201) {
            showMessage("¡Usuario registrado con éxito!", true);
            userForm.reset(); // Limpiar inputs
            fetchUsuarios();  // Refrescar la tabla automáticamente
        } else {
            throw new Error("No se pudo registrar el usuario en el servidor");
        }

    } catch (error) {
        console.error("Error en POST /usuarios:", error);
        showMessage("Hubo un error al registrar el usuario. Inténtalo de nuevo.", false);
    }
});

// --- HELPER: Mostrar mensajes en pantalla ---
function showMessage(text, isSuccess) {
    if (!text) {
        formMessage.className = "message hidden";
        return;
    }
    formMessage.textContent = text;
    formMessage.className = `message ${isSuccess ? 'success' : 'error'}`;
}

// --- HELPER: Prevenir ataques XSS simples al renderizar texto en la tabla ---
function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, 
        tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
    );
}

// --- INICIALIZACIÓN ---
// Ejecutar de inmediato al cargar la página web
document.addEventListener("DOMContentLoaded", () => {
    checkSystemHealth();
    fetchUsuarios();

    // Opcional: Verificar el estado del sistema automáticamente cada 30 segundos
    setInterval(checkSystemHealth, 30000);
});