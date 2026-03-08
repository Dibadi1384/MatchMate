//
//  WelcomeView.swift
//  MatchMate
//

import SwiftUI

struct WelcomeView: View {
    @Binding var path: NavigationPath
    @EnvironmentObject var appState: AppState

    var body: some View {
        ZStack {
            Color("AppCream")
                .ignoresSafeArea()

            VStack(spacing: 24) {
                Image("Icon")
                    .resizable()
                    .scaledToFit()
                    .frame(width: 250, height: 250)
                    .foregroundStyle(.tint)

                Text("MatchMate")
                    .font(.largeTitle)
                    .fontWeight(.bold)

                Text("Behavior-Based Social Matching")
                    .font(.subheadline)
                    .foregroundColor(.gray)
                    .multilineTextAlignment(.center)

                Spacer().frame(height: 40)

                Button(action: { path.append(AuthStep.signUp) }) {
                    Text("Sign up")
                        .fontWeight(.semibold)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.accentColor)
                        .foregroundColor(.white)
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                }
                .padding(.horizontal, 32)

                Button(action: { path.append(AuthStep.login) }) {
                    Text("Login")
                        .fontWeight(.semibold)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.clear)
                        .foregroundColor(.accentColor)
                        .overlay(RoundedRectangle(cornerRadius: 12).stroke(Color.accentColor, lineWidth: 2))
                }
                .padding(.horizontal, 32)
            }
            .padding()
        }
        .navigationBarBackButtonHidden(true)
    }
}

#Preview {
    NavigationStack {
        WelcomeView(path: .constant(NavigationPath()))
            .environmentObject(AppState())
    }
}
