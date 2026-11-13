// 写了 cookie 但没写 Domain：只在当前子域有效。
export function savePref(key: string, value: string) {
  document.cookie = `${key}=${value}; Path=/`;
}
