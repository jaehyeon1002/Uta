using UnityEngine;
using System.Collections;

public class WebViewManager : MonoBehaviour
{
    // WebView 객체
    private WebViewObject webViewObject;
    
    // 웹 URL
    private string webUrl = "https://vocal-alchemy-mixer.lovable.app/";
    
    // 전체 화면으로 표시 (0 마진)
    private int marginLeft = 0;
    private int marginTop = 0;
    private int marginRight = 0;
    private int marginBottom = 0;

    void Start()
    {
        // 앱 시작 시 자동으로 웹뷰 로드
        StartCoroutine(InitWebView());
    }

    private IEnumerator InitWebView()
    {
        // 잠시 대기 (씬 로딩을 위해)
        yield return new WaitForSeconds(0.5f);
        
        // WebView 객체 생성
        webViewObject = (new GameObject("WebViewObject")).AddComponent<WebViewObject>();
        webViewObject.transform.SetParent(transform);
        
        // WebView 초기화
        webViewObject.Init(
            cb: (msg) => {
                Debug.Log($"WebView Message: {msg}");
            },
            err: (msg) => {
                Debug.LogError($"WebView Error: {msg}");
            },
            httpErr: (msg) => {
                Debug.LogError($"WebView HTTP Error: {msg}");
            },
            started: (msg) => {
                Debug.Log($"WebView Started: {msg}");
            },
            hooked: (msg) => {
                Debug.Log($"WebView Loaded: {msg}");
            },
            ld: (msg) => {
                Debug.Log($"WebView Load Complete: {msg}");
                // 로드가 완료되면 확실히 보이게 설정
                webViewObject.SetVisibility(true);
            },
            enableWKWebView: true
        );

        // 전체 화면으로 표시 (마진 0)
        webViewObject.SetMargins(marginLeft, marginTop, marginRight, marginBottom);
        
        // 하드웨어 가속 활성화
        webViewObject.SetCameraAccess(true);
        webViewObject.SetMicrophoneAccess(true);
        
        // 해상도 설정
        webViewObject.SetTextZoom(100);
        
        // URL 로드 및 표시
        webViewObject.LoadURL(webUrl);
        webViewObject.SetVisibility(true);
    }

    // 앱이 일시정지될 때 (홈 버튼 등으로 백그라운드로 갈 때)
    void OnApplicationPause(bool pauseStatus)
    {
        if (webViewObject != null)
        {
            // 앱이 일시정지되면 WebView도 일시정지
            webViewObject.SetVisibility(!pauseStatus);
        }
    }

    // 앱이 종료될 때
    void OnDestroy()
    {
        if (webViewObject != null)
        {
            webViewObject.SetVisibility(false);
            Destroy(webViewObject.gameObject);
            webViewObject = null;
        }
    }
} 