<template>
  <main class="relative min-h-screen w-full lg:grid lg:grid-cols-2">
    <!-- Mobile Background (Visible only on < lg) -->
    <div class="absolute inset-0 z-0 overflow-hidden bg-neutral-900 lg:hidden">
      <img
        src="@/assets/hero-pets.png"
        alt="Background"
        class="h-full w-full object-cover opacity-100"
      />
      <div class="absolute inset-0 bg-gradient-to-t from-neutral-900 via-neutral-900/80 to-primary-900/40 mix-blend-multiply"></div>
      <div class="absolute inset-0 bg-black/20 backdrop-blur-[2px]"></div>
    </div>

    <!-- Left Side: Form Container -->
    <div class="relative z-10 flex min-h-screen items-center justify-center p-4 sm:p-12 lg:min-h-0 lg:bg-white lg:p-16">
      <div class="w-full max-w-md space-y-8 rounded-3xl bg-white/95 p-8 shadow-2xl shadow-black/20 backdrop-blur-xl ring-1 ring-white/50 lg:bg-transparent lg:p-0 lg:shadow-none lg:ring-0">
        <slot />
        <p class="mt-8 text-center text-xs text-neutral-400 lg:text-neutral-400 text-neutral-500">
          Copyright &copy; {{ new Date().getFullYear() }} Metaway Petshop
        </p>
      </div>
    </div>

    <!-- Right Side: Decorative & Image (Desktop Only) -->
    <div class="relative hidden h-full flex-col justify-between overflow-hidden bg-neutral-900 px-12 py-16 text-white lg:flex">
      <!-- Background Image -->
      <img
        src="@/assets/hero-pets.png"
        alt="Pets felizes esperando por você"
        class="absolute inset-0 h-full w-full object-cover object-center opacity-100 transition-transform duration-700 hover:scale-105"
      />

      <!-- Gradient Overlay (Color Tint) -->
      <div class="absolute inset-0 bg-gradient-to-t from-neutral-900 via-neutral-900/60 to-primary-900/20 mix-blend-multiply"></div>
      
      <!-- Gradient Overlay (Bottom Fade) -->
      <div class="absolute inset-0 bg-gradient-to-t from-neutral-900 via-transparent to-transparent"></div>

      <!-- Brand Logo Area -->
      <div class="relative z-10">
        <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-white/10 ring-1 ring-white/20 backdrop-blur-md">
           <!-- Simple paw icon SVG -->
           <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-white"><path d="M10 5.172C10 3.782 8.423 2.679 6.5 3c-2.823.47-4.113 6.006-4 7 .08.703 1.725 1.722 3.656 1 1.261-.472 1.96-1.45 2.344-2.5"/><path d="M14.267 5.172c0-1.39 1.577-2.493 3.5-2.172 2.823.47 4.113 6.006 4 7-.08.703-1.725 1.722-3.656 1-1.261-.472-1.96-1.45-2.344-2.5"/><path d="M8 14v.5"/><path d="M16 14v.5"/><path d="M11.25 16.25h1.5L12 17l-.75-.75Z"/><path d="M4.42 11.247A13.153 13.153 0 0 0 4 14.556C4 18.728 7.582 22 12 22s8-3.272 8-7.444c0-1.128-.465-2.19-1.242-3.07"/></svg>
        </div>
      </div>

      <!-- Content -->
      <div class="relative z-10 max-w-lg">
        <h2 class="font-display text-4xl font-bold leading-tight tracking-tight text-white drop-shadow-sm">
          O melhor cuidado <br />
          <span class="text-primary-400">para o seu melhor amigo.</span>
        </h2>
        <p class="mt-6 text-lg leading-relaxed text-neutral-200 drop-shadow-sm">
          Gestão completa, intuitiva e moderna para o seu petshop. 
          Do agendamento ao financeiro, tudo em um só lugar.
        </p>

        <!-- Trust Badge -->
        <div class="mt-8 flex items-center gap-4 border-t border-white/20 pt-8 opacity-90">
          <div class="flex -space-x-3">
             <!-- Placeholder avatars -->
            <div class="flex h-8 w-8 items-center justify-center rounded-full bg-neutral-700 ring-2 ring-neutral-900 text-[10px] font-bold">JP</div>
            <div class="flex h-8 w-8 items-center justify-center rounded-full bg-neutral-600 ring-2 ring-neutral-900 text-[10px] font-bold">AM</div>
            <div class="flex h-8 w-8 items-center justify-center rounded-full bg-primary-600 ring-2 ring-neutral-900 text-[10px] font-bold">+2k</div>
          </div>
          <div class="text-sm font-medium text-white">
            <span class="text-primary-400">Confiam</span> na Metaway Petshop
          </div>
        </div>
      </div>
    </div>
  </main>
</template>
