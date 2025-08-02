<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="preconnect" href="https://fonts.gstatic.com/" crossorigin="" />
    <link
      rel="stylesheet"
      as="style"
      onload="this.rel='stylesheet'"
      href="https://fonts.googleapis.com/css2?display=swap&amp;family=Noto+Sans%3Awght%40400%3B500%3B700%3B900&amp;family=Public+Sans%3Awght%40400%3B500%3B700%3B900"
    />
    <title>EduBank</title>
    <link rel="icon" type="image/x-icon" href="data:image/x-icon;base64," />
    <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
  </head>
  <body>
    <div class="relative flex size-full min-h-screen flex-col bg-white group/design-root overflow-x-hidden" style='font-family: "Public Sans", "Noto Sans", sans-serif;'>
      <div class="layout-container flex h-full grow flex-col">
        <header class="flex items-center justify-between border-b border-solid border-b-[#f0f4f0] px-10 py-3">
          <div class="flex items-center gap-4 text-[#111811]">
            <div class="size-4">
              <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path
                  d="M4 42.4379C4 42.4379 14.0962 36.0744 24 41.1692C35.0664 46.8624 44 42.2078 44 42.2078L44 7.01134C44 7.01134 35.068 11.6577 24.0031 5.96913C14.0971 0.876274 4 7.27094 4 7.27094L4 42.4379Z"
                  fill="currentColor"
                ></path>
              </svg>
            </div>
            <h2 class="text-lg font-bold leading-tight tracking-[-0.015em]">EduBank</h2>
          </div>
          <div class="flex flex-1 justify-end gap-8">
            <div class="flex items-center gap-9">
              <a class="text-sm font-medium leading-normal" href="#">Inicio</a>
              <a class="text-sm font-medium leading-normal" href="#">Servicios</a>
              <a class="text-sm font-medium leading-normal" href="#">Acerca de</a>
            </div>
            <div class="flex gap-2">
              <a
                href="https://edubank.com/login"
                class="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-full h-10 px-4 bg-[#f0f4f0] text-[#111811] text-sm font-bold leading-normal tracking-[0.015em]"
              >
                <span class="truncate">Iniciar Sesión</span>
              </a>
            </div>
          </div>
        </header>
        <div class="px-40 flex flex-1 justify-center py-5">
          <div class="layout-content-container flex flex-col max-w-[960px] flex-1">
            <div class="@container">
              <div class="@[480px]:p-4">
                <div
                  class="flex min-h-[480px] flex-col gap-6 bg-cover bg-center bg-no-repeat @[480px]:gap-8 @[480px]:rounded-xl items-center justify-center p-4"
                  style='background-image: linear-gradient(rgba(0, 0, 0, 0.1) 0%, rgba(0, 0, 0, 0.4) 100%), url("https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=1350&q=80");'
                >
                  <div class="flex flex-col gap-2 text-center">
                    <h1 class="text-white text-4xl font-black leading-tight tracking-[-0.033em] @[480px]:text-5xl">
                      Bienvenido a EduBank
                    </h1>
                    <h2 class="text-white text-sm font-normal leading-normal @[480px]:text-base">
                      Tu plataforma para la educación financiera de estudiantes.
                    </h2>
                  </div>
                  <div class="flex-wrap gap-3 flex justify-center">
                    <a
                      href="https://edubank.com/login-docentes"
                      class="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-full h-10 px-4 bg-[#16ce16] text-[#111811] text-sm font-bold leading-normal tracking-[0.015em] @[480px]:h-12 @[480px]:px-5"
                    >
                      <span class="truncate">Iniciar Sesión (Docente)</span>
                    </a>
                    <a
                      href="https://edubank.com/login-admin"
                      class="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-full h-10 px-4 bg-[#f0f4f0] text-[#111811] text-sm font-bold leading-normal tracking-[0.015em] @[480px]:h-12 @[480px]:px-5"
                    >
                      <span class="truncate">Iniciar Sesión (Administrador)</span>
                    </a>
                  </div>
                </div>
              </div>
            </div>
            <!-- (Aquí puedes dejar el resto de secciones: características, footer, etc. Igual que tu código original) -->
          </div>
        </div>
        <footer class="flex justify-center">
          <div class="flex max-w-[960px] flex-1 flex-col">
            <footer class="flex flex-col gap-6 px-5 py-10 text-center @container">
              <div class="flex flex-wrap items-center justify-center gap-6 @[480px]:flex-row @[480px]:justify-around">
                <a class="text-[#638863] text-base font-normal leading-normal min-w-40" href="#">Política de Privacidad</a>
                <a class="text-[#638863] text-base font-normal leading-normal min-w-40" href="#">Términos de Servicio</a>
                <a class="text-[#638863] text-base font-normal leading-normal min-w-40" href="#">Contacto</a>
              </div>
              <p class="text-[#638863] text-base font-normal leading-normal">© 2024 EduBank. Todos los derechos reservados.</p>
            </footer>
          </div>
        </footer>
      </div>
    </div>
  </body>
</html>
