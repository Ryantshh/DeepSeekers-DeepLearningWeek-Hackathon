<template>
  <div
    class="flex flex-col items-center justify-center h-screen bg-gradient-to-br from-gray-900 to-gray-700 text-white">
    <h1 class="text-9xl font-extrabold text-red-500 drop-shadow-lg">404</h1>
    <p class="text-2xl md:text-3xl font-semibold mt-4">Oops! Page Not Found</p>
    <p class="text-lg text-gray-300 mt-2 max-w-lg text-center">
      The page you're looking for doesn't exist or has been moved.
    </p>
    <router-link to="/"
      class="mt-6 px-6 py-3 bg-blue-500 hover:bg-blue-600 transition duration-300 text-white font-semibold text-lg rounded-lg shadow-lg">
      Go Back Home
    </router-link>
  </div>
</template>
