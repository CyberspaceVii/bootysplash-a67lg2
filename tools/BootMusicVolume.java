import android.os.IBinder;
import android.os.SystemClock;
import java.lang.reflect.Method;

/** A bounded, boot-only audio-policy override. Never writes saved volume settings. */
public final class BootMusicVolume {
    private static final int MUSIC = 3, SPEAKER = 2;
    // A moderate speaker level, independent of the saved media volume.
    private static final float TARGET_DB = -15.6f;
    private static final Class<?> AUDIO;
    private static final Method GET, SET, DB, PROPERTY;
    static {
        try {
            AUDIO = Class.forName("android.media.AudioSystem");
            GET = AUDIO.getMethod("getStreamVolumeIndex", int.class, int.class);
            SET = AUDIO.getMethod("setStreamVolumeIndexAS", int.class, int.class, boolean.class, int.class);
            DB = AUDIO.getMethod("getStreamVolumeDB", int.class, int.class, int.class);
            PROPERTY = Class.forName("android.os.SystemProperties").getMethod("get", String.class);
        } catch (Exception error) { throw new ExceptionInInitializerError(error); }
    }
    private static int index() throws Exception { return (Integer) GET.invoke(null, MUSIC, SPEAKER); }
    private static float db(int index) throws Exception { return (Float) DB.invoke(null, MUSIC, index, SPEAKER); }
    private static void set(int index, boolean muted) throws Exception {
        int result = (Integer) SET.invoke(null, MUSIC, index, muted, SPEAKER);
        if (result != 0) throw new IllegalStateException("Audio policy rejected level: " + result);
    }
    private static String animation() throws Exception { return (String) PROPERTY.invoke(null, "init.svc.bootanim"); }
    private static int target() throws Exception {
        int selected = -1;
        float difference = Float.POSITIVE_INFINITY;
        for (int candidate = 1; candidate <= 25; candidate++) {
            float attenuation = db(candidate);
            if (!Float.isFinite(attenuation)) continue;
            float error = Math.abs(attenuation - TARGET_DB);
            if (error < difference) { difference = error; selected = candidate; }
        }
        if (selected < 0 || difference > 3) throw new IllegalStateException("Speaker curve unavailable");
        return selected;
    }
    private static Object service() throws Exception {
        Object binder = Class.forName("android.os.ServiceManager").getMethod("getService", String.class).invoke(null, "audio");
        if (binder == null) return null;
        return Class.forName("android.media.IAudioService$Stub").getMethod("asInterface", IBinder.class).invoke(null, binder);
    }
    private static int saved(Object service) throws Exception {
        return (Integer) Class.forName("android.media.IAudioService").getMethod("getStreamVolume", int.class).invoke(service, MUSIC);
    }
    private static boolean muted(Object service) throws Exception {
        return (Boolean) Class.forName("android.media.IAudioService").getMethod("isStreamMute", int.class).invoke(service, MUSIC);
    }
    public static void main(String[] args) throws Exception {
        boolean check = args.length == 1 && args[0].equals("--check");
        long deadline = SystemClock.elapsedRealtime() + 90000;
        if (!check) {
            while (!animation().equals("running")) {
                if (SystemClock.elapsedRealtime() > deadline) return;
                Thread.sleep(100);
            }
        }
        int original = index();
        boolean changed = false;
        try {
            int level = target();
            float curve = db(12);
            do {
                float currentCurve = db(12);
                if (currentCurve != curve) { level = target(); curve = currentCurve; }
                if (index() != level) {
                    changed = true;
                    set(level, false);
                    System.out.println("bootMs=" + SystemClock.elapsedRealtime() + " speakerIndex=" + index() + " dB=" + db(level));
                }
                if (check) {
                    if (index() != level) throw new IllegalStateException("Speaker level did not apply");
                    Object audio = service();
                    if (audio == null || saved(audio) != original) throw new IllegalStateException("Saved volume changed");
                    System.out.println("Live override and unchanged saved level verified");
                    break;
                }
                Thread.sleep(200);
            } while (animation().equals("running") && SystemClock.elapsedRealtime() < deadline);
        } finally {
            if (changed) {
                int restore = original;
                boolean restoreMute = false;
                try {
                    Object audio = service();
                    if (audio != null) { restore = saved(audio); restoreMute = muted(audio); }
                } catch (Exception error) { System.out.println("Using initial level for restoration"); }
                set(restore, restoreMute);
                if (index() != restore) throw new IllegalStateException("Speaker restoration failed");
                System.out.println("bootMs=" + SystemClock.elapsedRealtime() + " restoredSpeakerIndex=" + restore + " muted=" + restoreMute);
            }
        }
    }
}
