//
//  ContentView.swift
//  MatchMate
//

import SwiftUI

struct ContentView: View {
    @EnvironmentObject var appState: AppState
    @State private var authPath = NavigationPath()

    var body: some View {
        Group {
            if appState.isLoggedIn {
                HomeView()
            } else {
                NavigationStack(path: $authPath) {
                    WelcomeView(path: $authPath)
                        .navigationDestination(for: AuthStep.self) { step in
                            switch step {
                            case .signUp:
                                SignUpView(path: $authPath)
                            case .login:
                                LoginView(path: $authPath)
                            case .profileCreation:
                                ProfileCreationView(path: $authPath)
                            case .dataUpload:
                                DataUploadView(path: $authPath)
                            }
                        }
                }
            }
        }
    }
}

#Preview {
    ContentView()
        .environmentObject(AppState())
}
